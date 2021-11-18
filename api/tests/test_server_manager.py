from unittest.mock import MagicMock
from multiprocessing.connection import Listener
from server_manager import ServerManager
from database.models import Server
import socket
import pytest
import database.queries
import lua

with open('../common/test/test1.json') as f:
  test_server_config1 = f.read()

with open('../common/test/test2.json') as f:
  test_server_config2 = f.read()

test_server = Server(
  id=1,
  user=2,
  name='Test Server',
  region='region1',
  status='running',
  game_mode='CTF',
  server_config=test_server_config1
)

test_server2 = Server(
  id=2,
  user=4,
  name='Test Server2',
  region='region2',
  status='running',
  game_mode='CTF',
  server_config=test_server_config2
)

TEST_AUTH_KEY = 'test_auth_key'
TEST_NODES = { 'test_host': 'localhost' }
EMPTY_SYNC_MESSAGE = {'type': 'sync', 'payload': {}}


@pytest.fixture
def listener():
  # open listener on port 0 (os assigns) and then get the actual port
  listener = Listener(('localhost', 0), authkey=TEST_AUTH_KEY.encode())
  listener._listener._socket.settimeout(2)
  yield listener
  listener.close()


@pytest.fixture
def actual_port(listener):
  return listener.address[1]

def test_sync_empty(listener, actual_port, monkeypatch):
  monkeypatch.setattr(database.queries, "get_active_servers", lambda db,region: [])

  server_manager = ServerManager(
    nodes={ 'test_host': 'localhost' },
    port=actual_port,
    auth_key=TEST_AUTH_KEY,
    db_session=MagicMock()
  )
  server_manager.sync()

  with listener.accept() as conn:
    sync_message = conn.recv()
    conn.send(0)

  assert sync_message == EMPTY_SYNC_MESSAGE


def test_sync_multiple(listener: Listener, actual_port: int, monkeypatch):
  test_nodes = {
    'region1': 'localhost',
    'region2': 'localhost'
  }

  active = {
    'region1': [test_server],
    'region2': [test_server2]
  }

  name_to_test_lua = {
    'TEST1': 'TEST_LUA_1',
    'TEST2': 'TEST_LUA_2',
  }

  def mocked_active_servers(db, region):
    return active[region]
  
  monkeypatch.setattr(database.queries, 'get_active_servers', mocked_active_servers)

  def mocked_lua(config):
    return name_to_test_lua[config.display_name]

  monkeypatch.setattr(lua, 'to_lua', mocked_lua)
  
  server_manager = ServerManager(
    nodes=test_nodes,
    port=actual_port, 
    auth_key=TEST_AUTH_KEY,
    db_session=MagicMock
  )
  server_manager.sync()

  with listener.accept() as conn:
    assert conn.recv() == {'type': 'sync', 'payload': {1: 'TEST_LUA_1'}}
    conn.send(0)
  
  with listener.accept() as conn:
    assert conn.recv() == {'type': 'sync', 'payload': {2: 'TEST_LUA_2'}}
    conn.send(0)


def test_sync_rate_limit(listener, actual_port, monkeypatch):
  monkeypatch.setattr(database.queries, 'get_active_servers', lambda db,region: [])

  server_manager = ServerManager(
    nodes=TEST_NODES,
    port=actual_port,
    auth_key=TEST_AUTH_KEY,
    db_session=MagicMock(),
    rate_limit_secs=0 # don't rate limit syncs
  )
  server_manager.sync()

  with listener.accept() as conn:
    # server manager is blocked, request 100 syncs
    for i in range(100):
      server_manager.sync()

    assert conn.recv() == EMPTY_SYNC_MESSAGE
    conn.send(0)

  # expect 1 update
  with listener.accept() as conn:
    assert conn.recv() == EMPTY_SYNC_MESSAGE
    conn.send(0)
  
  # no more connections
  # listener._listener._socket.settimeout(5)
  with pytest.raises(socket.timeout):
    listener.accept()
  
    


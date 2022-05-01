import pytest

import requests
import time
from typing import Callable, Tuple
from unittest.mock import MagicMock, Mock, call, patch

from loguru import logger

from src.host_manager import HostManager
from src.database.models import Server
from src.database import queries as db_queries
from src import lua

TEST_PORT=23456;

with open('tests/examples/test1.json') as f:
  test_server_config1 = f.read()

with open('tests/examples/test2.json') as f:
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

TEST_NODES = { 'test_host': 'localhost' }
EMPTY_SYNC_MESSAGE = {'type': 'sync', 'payload': {}}


def wait_for(assertion: Callable[[], bool], wait_time=1, interval=0.001) -> Tuple[float, int]:
  """ wait for assertion to be true, if timeout assert false"""
  start_time = time.time()
  tries = 0
  while time.time() - start_time < wait_time:
    tries += 1
    result = assertion()
    if result:
      return (time.time() - start_time, tries)
    time.sleep(interval)
  return (time.time() - start_time, tries)

@pytest.fixture
def mock_requests():
  with patch('src.host_manager.requests') as mock:
    yield mock

def test_sync_empty(monkeypatch, mock_requests: Mock):
  monkeypatch.setattr(db_queries, "get_active_servers", lambda db,region: [])
  monkeypatch.setattr(db_queries, "get_admin_tribes_usernames", lambda db: [])

  mock = MagicMock()
  monkeypatch.setattr(requests, 'post', lambda *a, **k: mock)


  host_manager = HostManager(
    nodes={ 'test_host': 'localhost' },
    port=TEST_PORT,
    db_session=MagicMock()
  )
  host_manager.sync()

  wait_for(lambda: mock_requests.called)
  mock_requests.post.assert_called_once_with('http://localhost:23456/message', json=EMPTY_SYNC_MESSAGE)


def test_sync_multiple(monkeypatch, mock_requests: Mock):
  test_nodes = {
    'region1': 'hostname1',
    'region2': 'hostname2'
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
  
  monkeypatch.setattr(db_queries, 'get_active_servers', mocked_active_servers)
  monkeypatch.setattr(db_queries, "get_admin_tribes_usernames", lambda db: [])

  def mocked_lua(config, lua_settings):
    return name_to_test_lua[config.display_name]

  monkeypatch.setattr(lua, 'to_lua', mocked_lua)
  
  host_manager = HostManager(
    nodes=test_nodes,
    port=TEST_PORT, 
    db_session=MagicMock
  )
  host_manager.sync()

  wait_for(lambda: mock_requests.call_count == 2)
  mock_requests.assert_has_calls([
    call.post('http://hostname1:23456/message', json={'type': 'sync', 'payload': {1: 'TEST_LUA_1'}}),
    call.post('http://hostname2:23456/message', json= {'type': 'sync', 'payload': {2: 'TEST_LUA_2'}})
  ])


def test_sync_rate_limit(monkeypatch, mock_requests: Mock):
  monkeypatch.setattr(db_queries, 'get_active_servers', lambda db,region: [])
  monkeypatch.setattr(db_queries, "get_admin_tribes_usernames", lambda db: [])

  host_manager = HostManager(
    nodes=TEST_NODES,
    port=TEST_PORT,
    db_session=MagicMock(),
    rate_limit_secs=0 # don't rate limit syncs
  )
  
  calls = []
  def add_syncs(*args, **kwargs):
    # server manager is blocked, request 100 syncs
    if len(calls) == 0:
      for i in range(100):
        host_manager.sync()
    calls.append(call(*args, **kwargs))
    
  mock_requests.post.side_effect = add_syncs
  
  host_manager.sync()

  wait_for(lambda: len(calls) > 2, wait_time=2)
  assert calls == [
    call('http://localhost:23456/message', json=EMPTY_SYNC_MESSAGE),
    call('http://localhost:23456/message', json=EMPTY_SYNC_MESSAGE)
  ]

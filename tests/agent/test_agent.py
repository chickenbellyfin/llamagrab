import json
import os
import shutil
import tempfile
from unittest.mock import Mock, call

import pytest
from fastapi import status, FastAPI
from fastapi.testclient import TestClient

from common import hashing
from agent.lib.agent import Agent
from agent.lib.docker import ContainerMetadata, Docker
from agent.app import create_api

HEADER = {'Token': 'thetoken'}

@pytest.fixture
def mock_docker():
  return Mock()

@pytest.fixture
def temp_dir():
  dir = tempfile.mkdtemp()
  yield dir
  shutil.rmtree(dir)

@pytest.fixture
def agent(temp_dir, mock_docker) -> Agent:
  the_agent = Agent(
    data_dir=temp_dir,
    docker=mock_docker,
    max_concurrency=99,
    container_start_time_secs=-1 # sets the expiry in the past
  )
  return the_agent

@pytest.fixture
def test_client(agent):
  app = FastAPI()
  app.mount('/api', create_api(agent, 'thetoken'))
  return TestClient(app)


def test_start(test_client: TestClient):
  response = test_client.post('/api/ping', json={'type': 'ping'}, headers=HEADER)
  assert response.status_code == 200

def test_sync_empty(test_client: TestClient, mock_docker: Docker):

  mock_docker.status.return_value = {}
  response = test_client.post('/api/sync', json={}, headers=HEADER)

  assert response.status_code == 200
  mock_docker.status.assert_called()
  mock_docker.start_server.assert_not_called()
  mock_docker.stop_server.assert_not_called()

def test_sync_new_server(test_client: TestClient, mock_docker: Docker, temp_dir):

  mock_docker.status.return_value = {}
  response = test_client.post('/api/sync', json={
    1: {'lua': 'Test Lua 1'},
    5: {'lua': 'Test Lua 5', 'loginserver': 'loginserver.somewhere'}
  }, headers=HEADER)

  hash1 = hashing.md5({'lua': 'Test Lua 1'})
  hash2 = hashing.md5({'lua': 'Test Lua 5', 'loginserver': 'loginserver.somewhere'})

  assert response.status_code == 200

  mock_docker.status.assert_called()
  mock_docker.start_server.assert_has_calls([
    call(
      server_id=1, 
      offset=0, 
      abs_gamesettings=os.path.join(temp_dir, 'managed_gamesettings', 'server_1'), 
      abs_banlist=os.path.join(temp_dir, 'banlist.txt'),
      hash=hash1,
      loginserver=None
    ),
    call(
      server_id=5, 
      offset=2, 
      abs_gamesettings=os.path.join(temp_dir, 'managed_gamesettings', 'server_5'), 
      abs_banlist=os.path.join(temp_dir, 'banlist.txt'), 
      hash=hash2,
      loginserver='loginserver.somewhere'
    )
  ])
  mock_docker.stop_server.assert_not_called()

def test_host_abs_path(temp_dir, mock_docker):
  """Test that the host abs path gets sent to taserver docker container"""

  agent = Agent(
    data_dir=temp_dir,
    docker=mock_docker,
    host_abs_data_dir='/some/host/dir'
  )
  app = FastAPI()
  app.mount('/api', create_api(agent, 'thetoken'))
  test_client = TestClient(app)

  mock_docker.status.return_value = {}
  response = test_client.post('/api/sync', json={
    1: {'lua': 'Test Lua 1'},
    5: {'lua': 'Test Lua 5'}
  }, headers=HEADER)

  assert response.status_code == 200

  mock_docker.status.assert_called()
  mock_docker.start_server.assert_has_calls([
    call(
      server_id=1, 
      offset=0, 
      abs_gamesettings=os.path.join('/some/host/dir/managed_gamesettings', 'server_1'), 
      abs_banlist=os.path.join('/some/host/dir', 'banlist.txt'),
      hash=hashing.md5({'lua': 'Test Lua 1'}),
      loginserver=None
    ),
    call(
      server_id=5, 
      offset=2, 
      abs_gamesettings=os.path.join('/some/host/dir/managed_gamesettings', 'server_5'), 
      abs_banlist=os.path.join('/some/host/dir', 'banlist.txt'),
      hash=hashing.md5({'lua': 'Test Lua 5'}),
      loginserver=None
    )
  ])
  mock_docker.stop_server.assert_not_called()

  # lua is still written to the correct data_dir path
  with open(os.path.join(temp_dir, 'managed_gamesettings', 'server_1', 'serverconfig.lua')) as f:
    assert 'Test Lua 1' == f.read()

  with open(os.path.join(temp_dir, 'managed_gamesettings', 'server_5', 'serverconfig.lua')) as f:
    assert 'Test Lua 5' == f.read()

def test_sync_stop_server(test_client: TestClient, mock_docker: Docker):
  mock_docker.status.return_value = {}
  # create two servers
  response1 = test_client.post('/api/sync', json={
    1: {'lua': 'Test Lua 1'},
    5: {'lua': 'Test Lua 5'}
  }, headers=HEADER)

  assert response1.status_code == 200

  mock_docker.reset_mock()
  mock_docker.status.return_value = {
    1: ContainerMetadata(1, 0, hashing.md5({'lua': 'Test Lua 1'})),
    5: ContainerMetadata(1, 0, hashing.md5({'lua': 'Test Lua 5'}))
  }

  # Remove server 1
  response2 = test_client.post('/api/sync', json={
    5: {'lua': 'Test Lua 5'}
  }, headers=HEADER)
  assert response2.status_code == 200
  mock_docker.status.assert_called()
  mock_docker.start_server.assert_not_called()
  mock_docker.stop_server.assert_called_once_with(1)

def test_sync_update_server(test_client: TestClient, mock_docker: Docker, temp_dir):
  mock_docker.status.return_value = {}
  # create two servers
  response1 = test_client.post('/api/sync', json={
    1: {'lua': 'Test Lua 1'},
    5: {'lua': 'Test Lua 5'}
  }, headers=HEADER)
  assert response1.status_code == 200

  mock_docker.reset_mock()
  mock_docker.status.return_value = {
    1: ContainerMetadata(server_id=1, port_offset=0, hash=hashing.md5({'lua': 'Test Lua 1'})),
    5: ContainerMetadata(server_id=2, port_offset=2, hash=hashing.md5({'lua': 'Test Lua 5'}))
  }

  # update server 1
  response2 = test_client.post('/api/sync', json={
    1: {'lua': 'Test Lua 1 updated'},
    5: {'lua': 'Test Lua 5'}
  }, headers=HEADER)
  assert response2.status_code == 200

  mock_docker.status.assert_called()
  mock_docker.stop_server.assert_not_called()
  mock_docker.start_server.assert_called_once_with(
    server_id=1, 
    offset=0, 
    abs_gamesettings=os.path.join(temp_dir, 'managed_gamesettings', 'server_1'), 
    abs_banlist=os.path.join(temp_dir, 'banlist.txt'),
    hash=hashing.md5({'lua': 'Test Lua 1 updated'}),
    loginserver=None
  )

def test_sync_lua_written(test_client: TestClient, mock_docker: Docker, temp_dir):
  mock_docker.status.return_value = {}
  # create two servers
  response = test_client.post('/api/sync', json={
    1: {'lua': 'Test Lua 1'},
    5: {'lua': 'Test Lua 5'}
  }, headers=HEADER)

  assert response.status_code == 200

  with open(os.path.join(temp_dir, 'active_servers.json')) as f:
    assert {'1':{'lua': 'Test Lua 1'}, '5': {'lua': 'Test Lua 5'}} == json.load(f)

  with open(os.path.join(temp_dir, 'managed_gamesettings', 'server_1', 'serverconfig.lua')) as f:
    assert 'Test Lua 1' == f.read()

  with open(os.path.join(temp_dir, 'managed_gamesettings', 'server_5', 'serverconfig.lua')) as f:
    assert 'Test Lua 5' == f.read()


def test_bad_message_payload(test_client: TestClient, mock_docker: Docker):
  # create two servers
  response1 = test_client.post('/api/sync', json=0, headers=HEADER)

  assert response1.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

  # still running
  response2 = test_client.post('/api/ping', headers=HEADER)
  assert response2.status_code == 200

  mock_docker.status.assert_not_called()
  mock_docker.stop_server.assert_not_called()
  mock_docker.start_server.assert_not_called()

def test_get_status(test_client: TestClient, mock_docker: Docker):
  mock_docker.status.return_value = {}

  response = test_client.post('/api/sync', json={
    66: {'lua': 'Test Lua 66'},
    99: {'lua': 'Test Lua 99'}
  }, headers=HEADER)
  # the servers should be in agent.tasks with action=start

  mock_docker.status.return_value = {
    66: ContainerMetadata(server_id=66, port_offset=0, hash='hash1'),
    88: ContainerMetadata(server_id=99, port_offset=2, hash='hash1')
  }
  response = test_client.get('/api/status', headers=HEADER)

  assert response.status_code == 200
  assert response.json() == {
    '66': 'starting',
    '99': 'starting'
  }

def test_get_status_running(test_client: TestClient, mock_docker: Docker):
  mock_docker.status.return_value = {}

  response = test_client.post('/api/sync', json={
    66: {'lua': 'Test Lua 66'},
  }, headers=HEADER)
  # the server is agent.tasks with action=start
  
  mock_docker.status.return_value = {
    66: ContainerMetadata(server_id=66, port_offset=0, hash=hashing.md5({'lua': 'Test Lua 66'}))
  }
  response = test_client.post('/api/sync', json={
    66: {'lua': 'Test Lua 66'},
  }, headers=HEADER)
  # the second sync causes agent to expire the 'start' task
  # now server_66 is running in docker and not starting in agent tasks

  response = test_client.get('/api/status', headers=HEADER)

  assert response.status_code == 200
  assert response.json() == {
    '66': 'running'
  }

def test_get_status_restarting(test_client: TestClient, mock_docker: Docker):
  mock_docker.status.return_value = {}

  mock_docker.status.return_value = {
    66: ContainerMetadata(server_id=66, port_offset=0, hash='differenthash')
  }
  response = test_client.post('/api/sync', json={
    66: {'lua': 'Test Lua 66'},
  }, headers=HEADER)
  # the server is agent.tasks with action=restart since the running hash won't match the sync
  

  response = test_client.get('/api/status', headers=HEADER)

  assert response.status_code == 200
  assert response.json() == {
    '66': 'restarting'
  }

def test_update_banlist(test_client: TestClient, temp_dir: str):
  banlist = os.path.join(temp_dir, 'banlist.txt')
  with open(banlist) as f:
    assert f.read() == ''
  response1 = test_client.post(
    '/api/banlist',
    json=['1.1.1.1', '0.255.6.98', '43.46.46.1/24'],
    headers=HEADER
  )

  assert response1.status_code == status.HTTP_200_OK
  with open(banlist) as f:
    assert f.read() == '1.1.1.1\n0.255.6.98\n43.46.46.1/24\n'

  response2 = test_client.post(
    '/api/banlist',
    json=['2.2.2.2', '3.3.3.3'],
    headers=HEADER
  )

  assert response2.status_code == status.HTTP_200_OK
  with open(banlist) as f:
    assert f.read() == '2.2.2.2\n3.3.3.3\n'

def test_update_banlist_invalid(test_client: TestClient, temp_dir: str):
  banlist = os.path.join(temp_dir, 'banlist.txt')
  with open(banlist) as f:
    assert f.read() == ''
  response1 = test_client.post(
    '/api/banlist',
    json=['1.1.1.1', 'abcde'],
    headers=HEADER
  )
  assert response1.status_code == status.HTTP_400_BAD_REQUEST
  with open(banlist) as f:
    assert f.read() == ''

def test_unauthorized(test_client: TestClient, mock_docker: Docker):
  # no token
  ping_res = test_client.post('/api/ping', headers={})
  assert ping_res.status_code == 401

  sync_res = test_client.post('/api/sync', json={}, headers={})
  assert sync_res.status_code == 401

  status_res = test_client.get('/api/status', headers={})
  assert status_res.status_code == 401

  # bad token
  response2 = test_client.post('/api/ping', headers={'token': 'bad_token'})
  assert response2.status_code == 401

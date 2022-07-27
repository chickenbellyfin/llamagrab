import json
import os
import shutil
import tempfile
from unittest.mock import Mock, call

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from src.lib.agent import Agent
from src.lib.docker import Docker
from src.main import create_app

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
    docker=mock_docker
  )
  return the_agent

@pytest.fixture
def test_client(agent):
  return TestClient(create_app(agent, 'thetoken'))


def test_start(test_client: TestClient):
  response = test_client.post('/api/ping', json={'type': 'ping'}, headers=HEADER)
  assert response.ok

def test_sync_empty(test_client: TestClient, mock_docker: Docker):

  mock_docker.status.return_value = {}
  response = test_client.post('/api/sync', json={}, headers=HEADER)

  assert response.ok
  mock_docker.status.assert_called()
  mock_docker.start_server.assert_not_called()
  mock_docker.stop_server.assert_not_called()

def test_sync_new_server(test_client: TestClient, mock_docker: Docker, temp_dir):

  mock_docker.status.return_value = {}
  response = test_client.post('/api/sync', json={
    1: 'Test Lua 1',
    5: 'Test Lua 5'
  }, headers=HEADER)

  assert response.ok

  mock_docker.status.assert_called()
  mock_docker.start_server.assert_has_calls([
    call(1, 0, os.path.join(temp_dir, 'managed_gamesettings', 'server_1'), os.path.join(temp_dir, 'banlist.txt')),
    call(5, 2, os.path.join(temp_dir, 'managed_gamesettings', 'server_5'), os.path.join(temp_dir, 'banlist.txt'))
  ])
  mock_docker.stop_server.assert_not_called()

def test_host_abs_path(temp_dir, mock_docker):
  """Test that the host abs path gets sent to taserver docker container"""

  agent = Agent(
    data_dir=temp_dir,
    docker=mock_docker,
    host_abs_data_dir='/some/host/dir'
  )
  test_client = TestClient(create_app(agent, 'thetoken'))

  mock_docker.status.return_value = {}
  response = test_client.post('/api/sync', json={
    1: 'Test Lua 1',
    5: 'Test Lua 5'
  }, headers=HEADER)

  assert response.ok

  mock_docker.status.assert_called()
  mock_docker.start_server.assert_has_calls([
    call(1, 0, os.path.join('/some/host/dir/managed_gamesettings', 'server_1'), os.path.join('/some/host/dir', 'banlist.txt')),
    call(5, 2, os.path.join('/some/host/dir/managed_gamesettings', 'server_5'), os.path.join('/some/host/dir', 'banlist.txt'))
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
    1: 'Test Lua 1',
    5: 'Test Lua 5'
  }, headers=HEADER)

  assert response1.ok

  mock_docker.reset_mock()
  mock_docker.status.return_value = {
    1: 0,
    5: 2
  }

  # Remove server 1
  response2 = test_client.post('/api/sync', json={
    5: 'Test Lua 5'
  }, headers=HEADER)
  assert response2.ok
  mock_docker.status.assert_called()
  mock_docker.start_server.assert_not_called()
  mock_docker.stop_server.assert_called_once_with(1)

def test_sync_update_server(test_client: TestClient, mock_docker: Docker, temp_dir):
  mock_docker.status.return_value = {}
  # create two servers
  response1 = test_client.post('/api/sync', json={
    1: 'Test Lua 1',
    5: 'Test Lua 5'
  }, headers=HEADER)
  assert response1.ok

  mock_docker.reset_mock()
  mock_docker.status.return_value = {
    1: 0,
    5: 2
  }

  # update server 1
  response2 = test_client.post('/api/sync', json={
    1: 'Test Lua 1 updated',
    5: 'Test Lua 5'
  }, headers=HEADER)
  assert response2.ok

  mock_docker.status.assert_called()
  mock_docker.stop_server.assert_not_called()
  mock_docker.start_server.assert_called_once_with(
    1, 0, os.path.join(temp_dir, 'managed_gamesettings', 'server_1'), os.path.join(temp_dir, 'banlist.txt'))

def test_sync_lua_written(test_client: TestClient, mock_docker: Docker, temp_dir):
  mock_docker.status.return_value = {}
  # create two servers
  response = test_client.post('/api/sync', json={
    1: 'Test Lua 1',
    5: 'Test Lua 5'
  }, headers=HEADER)

  assert response.ok

  with open(os.path.join(temp_dir, 'active_servers.json')) as f:
    assert {'1':'Test Lua 1', '5': 'Test Lua 5'} == json.load(f)

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
  assert response2.ok

  mock_docker.status.assert_not_called()
  mock_docker.stop_server.assert_not_called()
  mock_docker.start_server.assert_not_called()

def test_get_status(test_client: TestClient, mock_docker: Docker):
  mock_docker.status.return_value = {
    66: 77,
    88: 99
  }
  response = test_client.get('/api/status', headers=HEADER)

  assert response.ok
  assert response.json() == [66, 88]

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

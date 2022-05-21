from fastapi import status
import pytest
import tempfile
from unittest.mock import Mock, call
import os
import json

from src.lib.agent import Agent
from src.lib.docker import Docker
import shutil
from fastapi.testclient import TestClient
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
  response = test_client.post('/message', json={'type': 'ping'}, headers=HEADER)
  assert response.ok

def test_sync_empty(test_client: TestClient, mock_docker: Docker):

  mock_docker.status.return_value = {}
  response = test_client.post('/message', json={
    'type': 'sync',
    'payload': {}
  }, headers=HEADER)

  assert response.ok
  mock_docker.status.assert_called()
  mock_docker.start_server.assert_not_called()
  mock_docker.stop_server.assert_not_called()

def test_sync_new_server(test_client: TestClient, mock_docker: Docker, temp_dir):

  mock_docker.status.return_value = {}
  response = test_client.post('/message', json={
    'type': 'sync',
    'payload': {
      1: 'Test Lua 1',
      5: 'Test Lua 5'
    }
  }, headers=HEADER)

  assert response.ok

  mock_docker.status.assert_called()
  mock_docker.start_server.assert_has_calls([
    call(1, 0, os.path.join(temp_dir, 'managed_gamesettings', 'server_1')),
    call(5, 2, os.path.join(temp_dir, 'managed_gamesettings', 'server_5'))
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
  response = test_client.post('/message', json={
    'type': 'sync',
    'payload': {
      1: 'Test Lua 1',
      5: 'Test Lua 5'
    }
  }, headers=HEADER)

  assert response.ok

  mock_docker.status.assert_called()
  mock_docker.start_server.assert_has_calls([
    call(1, 0, os.path.join('/some/host/dir/managed_gamesettings', 'server_1')),
    call(5, 2, os.path.join('/some/host/dir/managed_gamesettings', 'server_5'))
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
  response1 = test_client.post('/message', json={
    'type': 'sync',
    'payload': {
      1: 'Test Lua 1',
      5: 'Test Lua 5'
    }
  }, headers=HEADER)

  assert response1.ok

  mock_docker.reset_mock()
  mock_docker.status.return_value = {
    1: 0,
    5: 2
  }

  # Remove server 1
  response2 = test_client.post('/message', json={
    'type': 'sync',
    'payload': {
      5: 'Test Lua 5'
    }
  }, headers=HEADER)
  assert response2.ok
  mock_docker.status.assert_called()
  mock_docker.start_server.assert_not_called()
  mock_docker.stop_server.assert_called_once_with(1)

def test_sync_update_server(test_client: TestClient, mock_docker: Docker, temp_dir):
  mock_docker.status.return_value = {}
  # create two servers
  response1 = test_client.post('/message', json={
    'type': 'sync',
    'payload': {
      1: 'Test Lua 1',
      5: 'Test Lua 5'
    }
  }, headers=HEADER)
  assert response1.ok

  mock_docker.reset_mock()
  mock_docker.status.return_value = {
    1: 0,
    5: 2
  }

  # update server 1
  response2 = test_client.post('/message', json={
    'type': 'sync',
    'payload': {
      1: 'Test Lua 1 updated',
      5: 'Test Lua 5'
    }
  }, headers=HEADER)
  assert response2.ok

  mock_docker.status.assert_called()
  mock_docker.stop_server.assert_not_called()
  mock_docker.start_server.assert_called_once_with(
    1, 0, os.path.join(temp_dir, 'managed_gamesettings', 'server_1'))

def test_sync_lua_written(test_client: TestClient, mock_docker: Docker, temp_dir):
  mock_docker.status.return_value = {}
  # create two servers
  response = test_client.post('/message', json={
    'type': 'sync',
    'payload': {
      1: 'Test Lua 1',
      5: 'Test Lua 5'
    }
  }, headers=HEADER)

  assert response.ok

  with open(os.path.join(temp_dir, 'active_servers.json')) as f:
    assert {'1':'Test Lua 1', '5': 'Test Lua 5'} == json.load(f)

  with open(os.path.join(temp_dir, 'managed_gamesettings', 'server_1', 'serverconfig.lua')) as f:
    assert 'Test Lua 1' == f.read()

  with open(os.path.join(temp_dir, 'managed_gamesettings', 'server_5', 'serverconfig.lua')) as f:
    assert 'Test Lua 5' == f.read()


def test_bad_message_type(test_client: TestClient, mock_docker: Docker):
  # create two servers
  response = test_client.post('/message', json={
    'type': 'invalid_type',
    'payload': {}
  }, headers=HEADER)

  assert response.status_code == status.HTTP_400_BAD_REQUEST

  # still running
  # still running
  response2 = test_client.post('/message', json={
    'type': 'ping'
  }, headers=HEADER)
  assert response2.ok

  mock_docker.status.assert_not_called()
  mock_docker.stop_server.assert_not_called()
  mock_docker.start_server.assert_not_called()

def test_bad_message_payload(test_client: TestClient, mock_docker: Docker):
  # create two servers
  response1 = test_client.post('/message', json={
    'type': 'sync',
    'payload': 0
  }, headers=HEADER)

  assert response1.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

  # still running
  response2 = test_client.post('/message', json={
    'type': 'ping'
  }, headers=HEADER)
  assert response2.ok

  mock_docker.status.assert_not_called()
  mock_docker.stop_server.assert_not_called()
  mock_docker.start_server.assert_not_called()

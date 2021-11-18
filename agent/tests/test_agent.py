from typing import Tuple
import pytest
from multiprocessing.connection import Client
import tempfile
import unittest
from unittest.mock import Mock, call
import os
import json

from ..agent import Agent
from docker import Docker
import shutil

import logging

TEST_AUTH_KEY = 'test_auth_key'.encode()


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
  the_agent =Agent(
    gamesettings_dir=temp_dir,
    auth_key=TEST_AUTH_KEY,
    address=('localhost', 0),
    docker=mock_docker
  )
  the_agent.start()
  return the_agent


@pytest.fixture
def address(agent: Agent) -> Tuple[str, int]:
  return ('localhost', agent.listener.address[1])


def test_start(agent: Agent, address):
  connected = False
  with Client(address, authkey=TEST_AUTH_KEY) as conn:
    connected = True
    conn.send({'type': 'ping'})
    assert 0 == conn.recv()
  assert connected

def test_sync_empty(agent: Agent, address, mock_docker: Docker):
  mock_docker.status.return_value = {}

  with Client(address, authkey=TEST_AUTH_KEY) as conn:
    conn.send({
      'type': 'sync',
      'payload': {}
    })
    assert 0 == conn.recv()

  mock_docker.status.assert_called()
  mock_docker.start_server.assert_not_called()
  mock_docker.stop_server.assert_not_called()
  
def test_sync_new_server(agent: Agent, address, mock_docker: Docker, temp_dir):

  mock_docker.status.return_value = {}

  with Client(address, authkey=TEST_AUTH_KEY) as conn:
    conn.send({
      'type': 'sync',
      'payload': {
        1: 'Test Lua 1',
        5: 'Test Lua 5'
      }
    })
    assert 0 == conn.recv()

  mock_docker.status.assert_called()
  mock_docker.start_server.assert_has_calls([
    call(1, 0, os.path.join(temp_dir, 'server_1')),
    call(5, 2, os.path.join(temp_dir, 'server_5'))
  ])
  mock_docker.stop_server.assert_not_called()

def test_sync_stop_server(agent: Agent, address, mock_docker: Docker):
  mock_docker.status.return_value = {}

  # create two servers
  with Client(address, authkey=TEST_AUTH_KEY) as conn:
    conn.send({
      'type': 'sync',
      'payload': {
        1: 'Test Lua 1',
        5: 'Test Lua 5'
      }
    })
    assert 0 == conn.recv()

  mock_docker.reset_mock()
  mock_docker.status.return_value = {
    1: 0,
    5: 2
  }
  # Remove server 1
  with Client(address, authkey=TEST_AUTH_KEY) as conn:
    conn.send({
      'type': 'sync',
      'payload': {
        5: 'Test Lua 5'
      }
    })
    assert 0 == conn.recv()
  mock_docker.status.assert_called()
  mock_docker.start_server.assert_not_called()
  mock_docker.stop_server.assert_called_once_with(1)

def test_sync_update_server(agent: Agent, address, mock_docker: Docker, temp_dir):
  mock_docker.status.return_value = {}
  # create two servers
  with Client(address, authkey=TEST_AUTH_KEY) as conn:
    conn.send({
      'type': 'sync',
      'payload': {
        1: 'Test Lua 1',
        5: 'Test Lua 5'
      }
    })
    assert 0 == conn.recv()

  mock_docker.reset_mock()
  mock_docker.status.return_value = {
    1: 0,
    5: 2
  }

  # update server 1
  with Client(address, authkey=TEST_AUTH_KEY) as conn:
    conn.send({
      'type': 'sync',
      'payload': {
        1: 'Test Lua 1 updated',
        5: 'Test Lua 5'
      }
    })
    assert 0 == conn.recv()
  mock_docker.status.assert_called()    
  mock_docker.stop_server.assert_not_called()
  mock_docker.start_server.assert_called_once_with(
    1, 0, os.path.join(temp_dir, 'server_1'))

def test_sync_lua_written(agent: Agent, address, mock_docker: Docker, temp_dir):
  mock_docker.status.return_value = {}
  # create two servers
  with Client(address, authkey=TEST_AUTH_KEY) as conn:
    conn.send({
      'type': 'sync',
      'payload': {
        1: 'Test Lua 1',
        5: 'Test Lua 5'
      }
    })
    assert 0 == conn.recv()
  
  with open(os.path.join(temp_dir, 'active_servers.json')) as f:
    assert {'1':'Test Lua 1', '5': 'Test Lua 5'} == json.load(f)
    
  
  with open(os.path.join(temp_dir, 'server_1', 'serverconfig.lua')) as f:
    assert 'Test Lua 1' == f.read()
  
  with open(os.path.join(temp_dir, 'server_5', 'serverconfig.lua')) as f:
    assert 'Test Lua 5' == f.read()


def test_bad_message_type(agent: Agent, address, mock_docker: Docker):
  # create two servers
  with Client(address, authkey=TEST_AUTH_KEY) as conn:
    conn.send({
      'type': 'invalid_type',
      'payload': {}
    })
    assert 1 == conn.recv()


  # still running
  with Client(address, authkey=TEST_AUTH_KEY) as conn:
    conn.send({
      'type': 'ping'
    })
    assert 0 == conn.recv()

  mock_docker.status.assert_not_called()
  mock_docker.stop_server.assert_not_called()
  mock_docker.start_server.assert_not_called()

def test_bad_message_payload(agent: Agent, address, mock_docker: Docker):
  # create two servers
  with Client(address, authkey=TEST_AUTH_KEY) as conn:
    conn.send({
      'type': 'sync',
      'payload': 0
    })
    assert 1 == conn.recv()


  # still running
  with Client(address, authkey=TEST_AUTH_KEY) as conn:
    conn.send({
      'type': 'ping'
    })
    assert 0 == conn.recv()

  mock_docker.status.assert_not_called()
  mock_docker.stop_server.assert_not_called()
  mock_docker.start_server.assert_not_called()

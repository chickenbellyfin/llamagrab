import time
from typing import Callable, Tuple
from unittest.mock import MagicMock, Mock, call, patch

import pytest
import requests

from api import flags, lua
from api.database import queries as db_queries
from api.database.models import Server
from api.host_manager import HostManager
from api.schema.app_config import Region

TEST_PORT=23456;

with open('tests/api/examples/test1.json') as f:
  test_server_config1 = f.read()

with open('tests/api/examples/test2.json') as f:
  test_server_config2 = f.read()

test_server = Server(
  id=1,
  user=2,
  name='Test Server',
  region='region1',
  server_config=test_server_config1
)

test_server2 = Server(
  id=2,
  user=4,
  name='Test Server2',
  region='region2',
  server_config=test_server_config2
)

EMPTY_SYNC_MESSAGE = {}


@pytest.fixture
def mock_requests():
  with patch('api.host_manager.requests') as mock:
    yield mock

def test_sync_empty(monkeypatch, mock_requests: Mock):
  monkeypatch.setattr(db_queries, "get_active_servers", lambda db,region: [])
  monkeypatch.setattr(db_queries, "get_admin_tribes_usernames", lambda db: [])
  monkeypatch.setattr(flags, 'get_flag', lambda db,key: None)

  mock = MagicMock()
  monkeypatch.setattr(requests, 'post', lambda *a, **k: mock)


  host_manager = HostManager(
    regions={
      'test_host': Region(
        key='test_host',
        name='Test Host',
        host='http://localhost',
        token='test_token'
      )
    },
    port=TEST_PORT,
    database=MagicMock()
  )
  host_manager._do_sync()

  mock_requests.assert_has_calls([
    call.post(
      'http://localhost:23456/api/sync',
      json=EMPTY_SYNC_MESSAGE,
      headers={'Token': 'test_token'}
    )
  ])


def test_sync_multiple(monkeypatch, mock_requests: Mock):
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
  monkeypatch.setattr(flags, 'get_flag', lambda db,key: None)

  def mocked_lua(server, config, lua_settings):
    return name_to_test_lua[config.display_name]

  monkeypatch.setattr(lua, 'to_lua', mocked_lua)

  host_manager = HostManager(
    regions={
      'region1': Region(
        key='region1',
        name='Region 1',
        host='hostname1',
        token='r1token'
      ),      
      'region2': Region(
        key='region2',
        name='Region 2',
        host='hostname2',
        token='r2token'
      )
    },
    port=TEST_PORT,
    database=MagicMock()
  )
  host_manager._do_sync()

  mock_requests.assert_has_calls([
    call.post(
      'hostname1:23456/api/sync',
      json={1: {'lua': 'TEST_LUA_1', 'loginserver': None}},
      headers={'Token': 'r1token'}
    ),
    call.post().ok.__bool__(),
    call.post().json(),
    call.post().json().items(),
    call.post().json().items().__iter__(),
    call.post(
      'hostname2:23456/api/sync',
      json= {2: {'lua': 'TEST_LUA_2', 'loginserver': None}},
      headers={'Token': 'r2token'}
    ),
    call.post().ok.__bool__(),
    call.post().json(),
    call.post().json().items(),
    call.post().json().items().__iter__()
  ])

import asyncio
from typing import List
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from passlib.hash import argon2
from sqlalchemy.pool import StaticPool

from api import app
from api.auth import Auth
from api.database import database
from api.database.models import (Server, ServerEditor, ServerVersion, User,
                                 UserLimits)
from api.schema.app_config import Region
from api.schema.game_server_config import GameServerConfig

password_hashes = {
  'testpassword': argon2.hash('testpassword'),
  'testpassword2': argon2.hash('testpassword2'),
  'testadminpassword': argon2.hash('testadminpassword'),
  'testsuperpassword': argon2.hash('testsuperpassword'),
}

@pytest.fixture
def user_1():
  return User(
    id=0,
    username='testuser',
    password=password_hashes['testpassword'],
    tier='verified',
    limits=UserLimits(server_limit=1, active_limit=1)
  )

@pytest.fixture
def user_2():
  return User(
    id=1,
    username='testuser2',
    password=password_hashes['testpassword2'],
    tier='unverified',
    limits=UserLimits(server_limit=1, active_limit=1)
  )


@pytest.fixture
def user_admin():
  return User(
    id=2,
    username='testadmin',
    password=password_hashes['testadminpassword'],
    tier='admin',
    limits=UserLimits(server_limit=-1, active_limit=-1)
  )

@pytest.fixture
def user_super():
  return User(
    id=3,
    username='testsuper',
    password=password_hashes['testsuperpassword'],
    tier='super',
    limits=UserLimits(server_limit=-1, active_limit=-1)
  )

@pytest.fixture
def server1(user_1: User):
  return Server(
    id=0,
    user=user_1.id,
    name='Test Server 1',
    region='region1',
    game='tribes_ascend_ootb',
    server_config=GameServerConfig(
      password='testserverpassword',
      display_name='TestServer1Config'
    ).serialize(),
    updated_at=0,
    updated_by=user_1.id
  )

@pytest.fixture
def server2(user_admin: User):
  return Server(
    id=1,
    user=user_admin.id,
    name='Test Server 2',
    region='region2',
    game='tribes_ascend_ootb',
    server_config=GameServerConfig().serialize(),
    updated_at=0,
    updated_by=user_admin.id
  )

@pytest.fixture
def server1_version1(server1: Server, user_1):
  return ServerVersion(
    id=0,
    server_id=server1.id,
    server_config='{"displayName": "server1Version0"}',
    num_changes=-1,
    created_at=0,
    created_by=user_1.id
  )

@pytest.fixture
def server1_version2(server1: Server, user_1):
  return ServerVersion(
    id=1,
    server_id=server1.id,
    server_config='{"displayName": "server1Version2"}',
    num_changes=1,
    created_at=1,
    created_by=user_1.id
  )



@pytest.fixture
def server2_version1(server2: Server):
  return ServerVersion(
    id=2,
    server_id=server2.id,
    server_config=server2.server_config,
    num_changes=-1,
    created_at=0,
    created_by=1
  )


@pytest.fixture(autouse=True)
def populate_db(
  inmemory_db: database.Database,
  user_1,
  user_2,
  user_admin,
  user_super,
  server1,
  server2,
  server1_version1,
  server1_version2,
  server2_version1):
  with inmemory_db.session() as session:
    session.add(user_1)
    session.add(user_2)
    session.add(user_admin)
    session.add(user_super)
    session.add(server1)
    session.add(server2)
    session.add(server1_version1)
    session.add(server1_version2)
    session.add(server2_version1)
    session.add(ServerEditor(server_id=0, user_id=1))
    session.commit()


def login(mock_login_manager, user):
  f = asyncio.Future()
  f.set_result(user)
  mock_login_manager.return_value = f
  return user

@pytest.fixture
def login_user_1(mock_login_manager, user_1):
  return login(mock_login_manager, user_1)

@pytest.fixture
def login_user_2(mock_login_manager, user_2):
  return login(mock_login_manager, user_2)

@pytest.fixture
def login_user_admin(mock_login_manager, user_admin):
  return login(mock_login_manager, user_admin)

@pytest.fixture
def login_user_super(mock_login_manager, user_super):
  f = asyncio.Future()
  f.set_result(user_super)
  mock_login_manager.return_value = f
  return user_super


@pytest.fixture
def mock_login_manager():
  login_manager = MagicMock()
  return login_manager

@pytest.fixture
def test_auth(mock_login_manager, inmemory_db):
  return Auth(
    login_manager=mock_login_manager,
    database=inmemory_db
  )

@pytest.fixture
def test_regions() -> List[Region]:
  return {
    'region1': Region(key='region1', name="TestRegion1", host="http://r1url", token="r1token"),
    'region2': Region(key='region2', name="TestRegion2", host="http://r2url", token="r2token")
  }

@pytest.fixture
def db_session(inmemory_db: database.Database):
  return inmemory_db.session()

@pytest.fixture
def inmemory_db():
  # sqlite will be inmemory if path is empty
  return database.Database('', '', poolclass=StaticPool)

@pytest.fixture
def should_sync(host_manager):
  yield host_manager
  host_manager.sync.assert_called_once()

@pytest.fixture
def host_manager():
  return MagicMock()

@pytest.fixture
def status_manager():
  mock = MagicMock()
  mock.get_server_status.return_value = 'offline'
  mock.get_region_status = False
  return mock

@pytest.fixture
def mock_audit_log():
  return MagicMock()

@pytest.fixture
def test_app(
  test_auth,
  inmemory_db,
  test_regions,
  host_manager,
  status_manager,
  mock_audit_log):
  api = app.create_app(
    db_instance=inmemory_db,
    auth=test_auth,
    host_manager=host_manager,
    status_manager=status_manager,
    regions=test_regions,
    ip_log_db=None,
    loginservers=[],
    audit=mock_audit_log
  )
  top_level = FastAPI()
  top_level.mount('/api', api)
  return top_level

@pytest.fixture
def test_client(test_app):
  return TestClient(test_app)

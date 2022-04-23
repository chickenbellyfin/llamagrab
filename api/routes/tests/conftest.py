import pytest

import asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from passlib.hash import argon2
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm.session import Session
from unittest.mock import MagicMock

import app
from database.database import Database
from database import database, models
from schema.game_server_config import GameServerConfig


@pytest.fixture
def server1(user: models.User):
  return models.Server(
    id=0,
    user=user.id,
    name='Test Server 1',
    region='region1',
    status='stopped',
    game_mode='CTF',
    server_config=GameServerConfig(
      display_name='TestServer1Config'
    ).serialize(),
    updated_at=0,
    updated_by=user.id
  )

@pytest.fixture
def server1_version(server1: models.Server):
  return models.ServerVersion(
    id=0,
    server_id=server1.id,
    server_config='server1version1',
    num_changes=-1,
    created_at=0,
    created_by=0
  )

@pytest.fixture
def server1_version2(server1: models.Server):
  return models.ServerVersion(
    id=2,
    server_id=server1.id,
    server_config='server1version2',
    num_changes=1,
    created_at=1,
    created_by=0
  )


@pytest.fixture
def server2(admin_user: models.User):
  return models.Server(
    id=1,
    user=admin_user.id,
    name='Test Server 2',
    region='region2',
    status='stopped',
    game_mode='CTF',
    server_config=GameServerConfig().serialize(),
    updated_at=0,
    updated_by=admin_user.id
  )

@pytest.fixture
def server2_version(server2: models.Server):
  return models.ServerVersion(
    id=1,
    server_id=server2.id,
    server_config=server2.server_config,
    num_changes=-1,
    created_at=0,
    created_by=1
  )


@pytest.fixture
def add_servers(db_session: Session, server1, server2, server1_version, server1_version2, server2_version):
  db_session.add(server1)
  db_session.add(server2)
  db_session.add(server1_version)
  db_session.add(server1_version2)
  db_session.add(server2_version)
  db_session.add(models.ServerEditor(server_id=0, user_id=1))
  db_session.commit()


@pytest.fixture
def user():
  return models.User(
    id=0,
    username='testuser',
    password=argon2.hash('testpassword'),
    tier='verified',
    limits=models.UserLimits(server_limit=1, active_limit=1)
  )


@pytest.fixture
def admin_user():
  return models.User(
    id=1,
    username='testadmin',
    password=argon2.hash('testadminpassword'),
    tier='admin',    
    limits=models.UserLimits(server_limit=-1, active_limit=-1)
  )

@pytest.fixture
def super_user():
  return models.User(
    id=2,
    username='testsuper',
    password=argon2.hash('testsuperpassword'),
    tier='super',    
    limits=models.UserLimits(server_limit=-1, active_limit=-1)
  )


@pytest.fixture
def logged_in_user(mock_login_manager, user):
  """
  Sets up the LoginManager with a user(role=user) and return the user object
  """
  f = asyncio.Future()
  f.set_result(user)
  mock_login_manager.return_value = f
  return user

@pytest.fixture
def logged_in_admin(mock_login_manager, admin_user):
  """
  Sets up the LoginManager with a user(role=admin) and return the user object
  """
  f = asyncio.Future()
  f.set_result(admin_user)
  mock_login_manager.return_value = f
  return admin_user

@pytest.fixture
def logged_in_super(mock_login_manager, super_user):
  """
  Sets up the LoginManager with a user(role=admin) and return the user object
  """
  f = asyncio.Future()
  f.set_result(super_user)
  mock_login_manager.return_value = f
  return super_user
  

@pytest.fixture
def mock_login_manager():
  login_manager = MagicMock()
  return login_manager

@pytest.fixture
def test_regions():
  return {
    'region1': 'TestRegion1',
    'region2': 'TestRegion2'
  }

@pytest.fixture
def db_session(inmemory_db: Database):
  session = inmemory_db.SessionFactory()
  yield session
  session.close()

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
def test_app(
  mock_login_manager,
  inmemory_db,
  test_regions,
  host_manager):
  api = app.create_app(
    db_instance=inmemory_db,
    login_manager=mock_login_manager,
    host_manager=host_manager,
    regions=test_regions
  )
  top_level = FastAPI()
  top_level.mount('/api', api)
  return top_level

@pytest.fixture
def test_client(test_app):
  return TestClient(test_app)
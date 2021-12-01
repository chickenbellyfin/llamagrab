from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from unittest.mock import MagicMock
import asyncio
from database.models import UserLimits
from database.database import Database
from database import database, models
from sqlalchemy.pool import StaticPool
from passlib.hash import argon2

import app


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
def logged_in_user(mock_login_manager, user):
  """
  Sets up the LoginManager with a user(role=user) and return the user object
  """
  f = asyncio.Future()
  f.set_result(user)
  mock_login_manager.return_value = f
  return user

@pytest.fixture
def logged_in_admin(mock_login_manager):
  """
  Sets up the LoginManager with a user(role=admin) and return the user object
  """
  admin_user = models.User(
    id=1,
    username='testadmin',
    password=argon2.hash('testadminpassword'),
    tier='admin',    
    limits=models.UserLimits(server_limit=-1, active_limit=-1)
  )
  f = asyncio.Future()
  f.set_result(admin_user)
  mock_login_manager.return_value = f
  return admin_user

@pytest.fixture
def logged_in_super(mock_login_manager):
  """
  Sets up the LoginManager with a user(role=admin) and return the user object
  """
  super_user = models.User(
    id=2,
    username='testsuper',
    password=argon2.hash('testsuperpassword'),
    tier='super',    
    limits=models.UserLimits(server_limit=-1, active_limit=-1)
  )
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
    'region1': 'host1',
    'region2': 'host2'
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
def test_app(
  mock_login_manager,
  inmemory_db,
  test_regions):
  api = app.create_app(
    db_instance=inmemory_db,
    login_manager=mock_login_manager,
    server_manager=MagicMock(),
    regions=test_regions
  )
  top_level = FastAPI()
  top_level.mount('/api', api)
  return top_level

@pytest.fixture
def test_client(test_app):
  return TestClient(test_app)
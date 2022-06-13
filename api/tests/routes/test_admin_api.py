import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm.session import Session
from src.database import models


@pytest.fixture
def user_to_verify(db_session: Session):
  user = models.User(
    id=55,
    username='usertoverify',
    password='',
    tier='unverified',
    limits=models.UserLimits(server_limit=1, active_limit=1)
  )
  db_session.add(user)
  db_session.commit()
  return user

@pytest.fixture
def user_to_admin(db_session: Session):
  user = models.User(
    id=77,
    username='usertoadmin',
    password='',
    tier='verified',
    limits=models.UserLimits(server_limit=1, active_limit=1)
  )
  db_session.add(user)
  db_session.commit()
  return user

@pytest.fixture
def user_to_unadmin(db_session: Session):
  user = models.User(
    id=88,
    username='usertounadmin',
    password='',
    tier='admin',
    limits=models.UserLimits(server_limit=1, active_limit=1)
  )
  db_session.add(user)
  db_session.commit()
  return user

def test_verify_user(test_client: TestClient, login_user_admin, user_to_verify, db_session: Session):
  response = test_client.post('/api/admin/verify_user/55')
  assert response.status_code == status.HTTP_200_OK
  db_user = db_session.query(models.User).filter_by(id=55).first()
  assert db_user.tier == 'verified'
  assert db_user.limits.server_limit == 5
  assert db_user.limits.active_limit == 2


def test_verify_user_not_admin(test_client: TestClient, login_user_1, user_to_verify):
  response = test_client.post('/api/admin/verify_user/55')
  assert response.status_code == status.HTTP_403_FORBIDDEN

def test_verify_user_already_verified(test_client: TestClient, login_user_admin, user_to_verify, db_session: Session):
  user_to_verify.tier = 'admin'
  db_session.commit()
  response = test_client.post('/api/admin/verify_user/55')
  assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_verify_user_doesnt_exist(test_client: TestClient, login_user_admin):
  response = test_client.post('/api/admin/verify_user/55')
  assert response.status_code == status.HTTP_404_NOT_FOUND

def test_make_admin(test_client: TestClient, login_user_super, user_to_admin, db_session: Session):
  response = test_client.post('/api/admin/make_admin/77')
  assert response.status_code == status.HTTP_200_OK
  db_user = db_session.query(models.User).filter_by(id=77).first()
  assert db_user.tier == 'admin'
  assert db_user.limits.server_limit is None
  assert db_user.limits.active_limit is None

def test_make_admin_not_super(test_client: TestClient, login_user_admin, user_to_admin):
  response = test_client.post('/api/admin/make_admin/77')
  assert response.status_code == status.HTTP_403_FORBIDDEN

def test_make_admin_doesnt_exist(test_client: TestClient, login_user_super):
  response = test_client.post('/api/admin/make_admin/77')
  assert response.status_code == status.HTTP_404_NOT_FOUND

def test_make_admin_already_admin(test_client: TestClient, login_user_super, user_to_admin, db_session: Session):
  user_to_admin.tier = 'admin'
  db_session.commit()
  response = test_client.post('/api/admin/make_admin/77')
  assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_remove_admin(test_client: TestClient, login_user_super, user_to_unadmin, db_session: Session):
  response = test_client.delete('/api/admin/make_admin/88')
  assert response.status_code == status.HTTP_200_OK
  db_user = db_session.query(models.User).filter_by(id=88).first()
  assert db_user.tier == 'verified'
  assert db_user.limits.server_limit == 5
  assert db_user.limits.active_limit == 2

def test_remove_admin_not_super(test_client: TestClient, login_user_admin):
  response = test_client.delete('/api/admin/make_admin/88')
  assert response.status_code == status.HTTP_403_FORBIDDEN

def test_remove_admin_not_admin(test_client: TestClient, login_user_super, user_to_unadmin, db_session: Session):
  user_to_unadmin.tier = 'verified'
  db_session.commit()
  response = test_client.delete('/api/admin/make_admin/88')
  assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_remove_admin_doesnt_exist(test_client: TestClient, login_user_super):
  response = test_client.delete('/api/admin/make_admin/123')
  assert response.status_code == status.HTTP_404_NOT_FOUND

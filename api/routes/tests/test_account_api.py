


from fastapi_login.fastapi_login import LoginManager
from sqlalchemy.orm.session import Session
from starlette.testclient import TestClient
from fastapi import status
from database.models import UserLimits
from database import models
import time

def test_get_user(test_client: TestClient, logged_in_user, db_session: Session):
  db_session.add(logged_in_user)
  db_session.commit()
  response = test_client.get('/api/account/user')
  assert response.json() == {
    'id': 0,
    'username':
    'testuser',
    'tier':'verified',
    'limits': {
      'serverLimit': 1,
      'activeLimit': 1,
      'serverCount': 0
    },
    'tribesUsername': None
  }


def test_login(test_client: TestClient, mock_login_manager: LoginManager, db_session: Session, user: models.User):
  db_session.add(user)
  db_session.commit()
  mock_login_manager.create_access_token.return_value = 'test_access_token'

  response = test_client.post(
    '/api/account/login', 
    json={'username':'testuser', 'password': 'testpassword'}
  )

  assert response.json() == { 'access_token': 'test_access_token' }

def test_login_doesnt_exist(test_client: TestClient, mock_login_manager: LoginManager, db_session: Session, user: models.User):
  response = test_client.post(
    '/api/account/login', 
    json={'username':'idontexist', 'password': 'neitherdoi'}
  )
  assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_login_wrong_password(test_client: TestClient, mock_login_manager: LoginManager, db_session: Session, user: models.User):
  db_session.add(user)
  db_session.commit()
  mock_login_manager.create_access_token.return_value = 'test_access_token'

  response = test_client.post(
    '/api/account/login', 
    json={'username':'testuser', 'password': 'wrongpassword'}
  )

  assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_account(test_client: TestClient, db_session: Session):
  response = test_client.post('/api/account/create', json={
    'username': 'testuser2',
    'password': 'testpassword2'
  })
  assert response.status_code == status.HTTP_200_OK
  db_user = db_session.query(models.User).filter_by(username='testuser2').first()
  assert db_user is not None
  assert db_user.tier == 'unverified'
  assert db_user.limits.server_limit == 1
  assert db_user.limits.active_limit == 1
  

def test_create_second_account(test_client: TestClient, db_session: Session):
  response = test_client.post('/api/account/create', json={
    'username': 'testuser2',
    'password': 'testpassword2',
  })
  assert response.status_code == status.HTTP_200_OK
  
  # second one fails
  response = test_client.post('/api/account/create', json={
    'username': 'testuser3',
    'password': 'testpassword3',
  })
  assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS


def test_create_account_exists(test_client: TestClient, db_session: Session, user: models.User):
  db_session.add(user)
  db_session.commit() 
  response = test_client.post('/api/account/create', json={
    'username': 'testuser',
    'password': 'notthetestpassword',
  })
  assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_change_password(test_client: TestClient, db_session: Session, logged_in_user: models.User):
  response = test_client.post('/api/account/change_password', json={
    'currentPassword': 'testpassword',
    'newPassword': 'password123'
  })

  assert response.status_code == status.HTTP_200_OK
  
  # try to login with old password, should fail
  login_old_password = test_client.post(
    '/api/account/login', 
    json={'username':'testuser', 'password': 'testpassword'}
  )
  assert login_old_password.status_code == status.HTTP_401_UNAUTHORIZED

  # try to login with new password, should succeed
  login_old_password = test_client.post(
    '/api/account/login', 
    json={'username':'testuser', 'password': 'password123'}
  )
  assert login_old_password.status_code == status.HTTP_200_OK

# user is logged in but fails to confirm their old password
def test_change_password_bad_password(test_client: TestClient, db_session: Session, logged_in_user: models.User):
  response = test_client.post('/api/account/change_password', json={
    'currentPassword': 'testpasswordwrong',
    'newPassword': 'password123'
  })
  assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_user(test_client: TestClient, logged_in_super: models.User, user, add_servers, db_session: Session):
  db_session.add(user)
  db_session.commit()

  response = test_client.delete('/api/account/0')
  assert response.status_code == status.HTTP_200_OK
  assert db_session.query(models.User).filter(models.User.id == 0).first() == None
  assert db_session.query(models.UserLimits).filter(models.UserLimits.user_id == 0).first() == None
  assert list(db_session.query(models.Server).filter(models.Server.user == 0).all()) == []
  # the other server should still be there
  assert list(db_session.query(models.Server).all()) != []


def test_delete_user_not_found(test_client: TestClient, logged_in_super: models.User, user, add_servers, db_session: Session):
  db_session.add(user)
  db_session.commit()

  response = test_client.delete('/api/account/45')
  assert response.status_code == status.HTTP_404_NOT_FOUND
  assert db_session.query(models.User).filter(models.User.id == 0).first() != None


def test_delete_not_super(test_client: TestClient, logged_in_admin: models.User, user, add_servers, db_session: Session):
  db_session.add(user)
  db_session.commit()

  response = test_client.delete('/api/account/0')
  assert response.status_code == status.HTTP_403_FORBIDDEN
  assert db_session.query(models.User).filter(models.User.id == 0).first() != None
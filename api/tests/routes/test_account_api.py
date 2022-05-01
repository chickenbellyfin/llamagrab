from fastapi import status
from fastapi_login.fastapi_login import LoginManager
from starlette.testclient import TestClient
from sqlalchemy.orm.session import Session

from src.database.models import User, UserLimits, Server

def test_get_user(test_client: TestClient, login_user_1):
  response = test_client.get('/api/account/user')
  assert response.json() == {
    'id': 0,
    'username':
    'testuser',
    'tier':'verified',
    'limits': {
      'serverLimit': 1,
      'activeLimit': 1,
      'serverCount': 1
    },
    'tribesUsername': None
  }


def test_login(test_client: TestClient, mock_login_manager: LoginManager):
  mock_login_manager.create_access_token.return_value = 'test_access_token'

  response = test_client.post(
    '/api/account/login', 
    json={'username':'testuser', 'password': 'testpassword'}
  )

  assert response.json() == { 'access_token': 'test_access_token' }

def test_login_doesnt_exist(test_client: TestClient):
  response = test_client.post(
    '/api/account/login', 
    json={'username':'idontexist', 'password': 'neitherdoi'}
  )
  assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_login_wrong_password(test_client: TestClient, mock_login_manager: LoginManager):
  mock_login_manager.create_access_token.return_value = 'test_access_token'
  response = test_client.post(
    '/api/account/login', 
    json={'username':'testuser', 'password': 'wrongpassword'}
  )
  assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_create_account(test_client: TestClient, db_session: Session):
  response = test_client.post('/api/account/create', json={
    'username': 'testuser3',
    'password': 'testpassword3'
  })
  assert response.status_code == status.HTTP_200_OK
  db_user = db_session.query(User).filter_by(username='testuser3').first()
  assert db_user is not None
  assert db_user.tier == 'unverified'
  assert db_user.limits.server_limit == 1
  assert db_user.limits.active_limit == 1
  
def test_create_second_account(test_client: TestClient):
  response = test_client.post('/api/account/create', json={
    'username': 'testuser3',
    'password': 'testpassword3',
  })
  assert response.status_code == status.HTTP_200_OK
  
  # second one fails
  response2 = test_client.post('/api/account/create', json={
    'username': 'testuser4',
    'password': 'testpassword4',
  })
  assert response2.status_code == status.HTTP_429_TOO_MANY_REQUESTS

def test_create_second_account_reverse_proxied(test_client: TestClient):
  """
  create a user with x-forwarded-for IP -> ok
  Create a user with a normal request -> ok
  create a user with same x-forwarded-for IP -> 429
  """
  response = test_client.post(
    '/api/account/create', 
    json={
      'username': 'testuser3',
      'password': 'testpassword3',
    }, 
    headers={'X-Forwarded-For': '1.2.3.4'}
  )
  assert response.status_code == status.HTTP_200_OK
  
  response2 = test_client.post(
    '/api/account/create', 
    json={
      'username': 'testuser4',
      'password': 'testpassword4',
    }
  )
  assert response2.status_code == status.HTTP_200_OK
  
  # second one fails since client ip (forwarded) matches first account
  response3 = test_client.post(
    '/api/account/create', 
    json={
      'username': 'testuser5',
      'password': 'testpassword5',
    }, 
    headers={'X-Forwarded-For': '1.2.3.4'}
  )
  assert response3.status_code == status.HTTP_429_TOO_MANY_REQUESTS


def test_create_account_exists(test_client: TestClient, user_1: User):
  response = test_client.post('/api/account/create', json={
    'username': user_1.username,
    'password': 'notthetestpassword',
  })
  assert response.status_code == status.HTTP_400_BAD_REQUEST
  assert response.json() == {'detail': 'User already exists'}

def test_change_password(test_client: TestClient, login_user_1: User):
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
def test_change_password_bad_password(test_client: TestClient, login_user_1: User):
  response = test_client.post('/api/account/change_password', json={
    'currentPassword': 'testpasswordwrong',
    'newPassword': 'password123'
  })
  assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_delete_user(test_client: TestClient, login_user_super, db_session: Session):
  response = test_client.delete('/api/account/0')
  assert response.status_code == status.HTTP_200_OK
  assert db_session.query(User).filter(User.id == 0).first() == None
  assert db_session.query(UserLimits).filter(UserLimits.user_id == 0).first() == None
  assert list(db_session.query(Server).filter(Server.user == 0).all()) == []
  # the other server should still be there
  assert list(db_session.query(Server).all()) != []

def test_delete_user_not_found(test_client: TestClient, db_session: Session, login_user_super):
  response = test_client.delete('/api/account/45')
  assert response.status_code == status.HTTP_404_NOT_FOUND
  assert db_session.query(User).filter(User.id == 0).first() != None


def test_delete_not_super(test_client: TestClient, login_user_admin: User, db_session: Session):
  response = test_client.delete('/api/account/0')
  assert response.status_code == status.HTTP_403_FORBIDDEN
  assert db_session.query(User).filter(User.id == 0).first() != None

def test_set_tribes_name(test_client: TestClient, db_session: Session, login_user_1):
  response = test_client.post('/api/account/set_tribes_name', json={
    'tribesUsername': 'the_user21342'
  })
  assert response.status_code == status.HTTP_200_OK
  assert db_session.query(User).filter(User.id == login_user_1.id).first().tribes_username == 'the_user21342'

def test_list_accounts(test_client: TestClient, login_user_admin):
  response = test_client.get('/api/accounts')
  assert response.status_code == status.HTTP_200_OK
  assert response.json() == [
    {
      'id': 0,
      'username': 'testuser',
      'tier': 'verified',
      'limits': {'serverLimit': 1, 'activeLimit': 1, 'serverCount': 1},
      'tribesUsername': None
    },
    {
      'id': 1,
      'username': 'testuser2',
      'tier': 'unverified',
      'limits': {'serverLimit': 1, 'activeLimit': 1, 'serverCount': 0},
      'tribesUsername': None
    },
    {
      'id': 2,
      'username': 'testadmin',
      'tier': 'admin',
      'limits': {'serverLimit': -1, 'activeLimit': -1, 'serverCount': 1},
      'tribesUsername': None
    },
    {
      'id': 3,
      'username': 'testsuper',
      'tier': 'super',
      'limits': {'serverLimit': -1, 'activeLimit': -1, 'serverCount': 0},
      'tribesUsername': None
    },
  ]

def test_list_users(test_client: TestClient, login_user_1):
  response = test_client.get('/api/users')
  assert response.status_code == status.HTTP_200_OK
  assert response.json() == [
    {'id': 0, 'username': 'testuser'},
    {'id': 1, 'username': 'testuser2'},
    {'id': 2, 'username': 'testadmin'},
    {'id': 3, 'username': 'testsuper'},
  ]


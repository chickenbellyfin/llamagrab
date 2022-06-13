from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm.session import Session
from src.database.models import Server, ServerEditor, ServerVersion, User


def _remove_nones(obj: dict):
  for key in obj.copy():
    if obj[key] is None:
      obj.pop(key)
  return obj

def test_get_server_settings(test_client: TestClient, login_user_1):
  response = test_client.get('/api/server/0/settings')
  assert response.status_code == status.HTTP_200_OK
  assert response.json() == {'region': 'region1', 'editors': [1], 'game': 'tribes_ascend_ootb'}

def test_get_server_settings_other_user(test_client: TestClient, login_user_1):
  # server 1 belongs to admin
  response = test_client.get('/api/server/1/settings')
  assert response.status_code == status.HTTP_403_FORBIDDEN

def test_get_server_settings_missing(test_client: TestClient, login_user_1):
  response = test_client.get('/api/server/4545/settings') # server does not exist
  assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_server_config(test_client: TestClient, login_user_1):
  response = test_client.get('/api/server/0/config')
  assert response.status_code == status.HTTP_200_OK
  assert _remove_nones(response.json()) == {
    'displayName': 'TestServer1Config',
    'password': 'testserverpassword'
  }

def test_set_server_settings(test_client: TestClient, login_user_1, should_sync):
  response = test_client.post('/api/server/0/settings', json={
    'region': 'region2',
    'editors': [3]
  })
  assert response.status_code == status.HTTP_200_OK
  get_response = test_client.get('/api/server/0/settings')
  assert get_response.status_code == status.HTTP_200_OK
  assert get_response.json() == {
    'region': 'region2',
    'editors': [3],
    'game': 'tribes_ascend_ootb'
  }

def test_set_server_settings_bad_region(test_client: TestClient, login_user_1):
  response = test_client.post('/api/server/0/settings', json={
    'region': 'not_a_region'
  })
  assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_set_server_settings_game_type(test_client: TestClient, login_user_1):
  response = test_client.post('/api/server/0/settings', json={
    'game': 'tribes_ascend_goty'
  })
  assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_set_server_editors_non_owner(test_client: TestClient, db_session: Session, login_user_2):
  db_session.add(ServerEditor(server_id=0, user_id=login_user_2.id))
  db_session.commit()
  response = test_client.post('/api/server/0/settings', json={
    'region': 'not_a_region',
    'editors': [0]
  })
  assert response.status_code == status.HTTP_403_FORBIDDEN
  assert response.json() == {'detail': 'User cannot modify editors of server'}

def test_set_server_editors_invalid_user(test_client: TestClient, login_user_1):
  test_client.post('/api/server/0/settings', json={
    'region': 'not_a_region',
    'editors': [2323] # this user does not exist
  })
  get_response = test_client.get('/api/server/0/settings')
  assert get_response.json().get('editors') == [1]

def test_set_server_config(test_client: TestClient, db_session: Session, login_user_1, should_sync):
  response = test_client.post('/api/server/0/config', json={
    'displayName': 'NewDisplayName'
  })
  assert response.status_code == status.HTTP_200_OK
  get_response = test_client.get('/api/server/0/config')
  assert get_response.status_code == status.HTTP_200_OK
  assert _remove_nones(get_response.json()) == {'displayName': 'NewDisplayName'}
  versions = db_session.query(ServerVersion).filter(ServerVersion.server_id == 0).all()
  assert len(versions) == 3

def test_create_server(test_client: TestClient, db_session: Session, login_user_2: User):
  response = test_client.put('/api/servers', json={
    'serverSettings': { 'region': 'region2', 'editors': [0], 'game': 'tribes_ascend_ootb'},
    'serverConfig': {'displayName': 'CreateTestServer1Config'}
  })

  assert response.status_code == status.HTTP_201_CREATED
  server_status = response.json()
  server_id = server_status['id']
  get_response = test_client.get(f'/api/server/{server_id}/config')
  assert get_response.status_code == status.HTTP_200_OK
  assert _remove_nones(get_response.json()) == {'displayName': 'CreateTestServer1Config'}
  get_response = test_client.get(f'/api/server/{server_id}/settings')
  assert get_response.status_code == status.HTTP_200_OK
  assert _remove_nones(get_response.json()) == {
    'region': 'region2',
    'editors': [0],
    'game': 'tribes_ascend_ootb'
  }
  versions = db_session.query(ServerVersion).filter(ServerVersion.server_id == server_id).all()
  assert len(versions) == 1

def test_create_server_limit(test_client: TestClient, db_session: Session, login_user_1: User):
  login_user_1.limits.server_limit = 0
  db_session.merge(login_user_1)
  db_session.commit()
  response = test_client.put('/api/servers', json={
    'serverSettings': { 'region': 'region2', 'game': 'tribes_ascend_goty' },
    'serverConfig': {'displayName': 'CreateTestServer1Config'}
  })

  assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
  assert response.json() == {'detail': 'Server limit reached for user'}

def test_create_server_bad_game_type(test_client: TestClient, db_session: Session, login_user_1: User):
  login_user_1.limits.server_limit = 0
  db_session.merge(login_user_1)
  db_session.commit()
  response = test_client.put('/api/servers', json={
    'serverSettings': { 'region': 'region2', 'game': 'unsupport_fake_game' },
    'serverConfig': {'displayName': 'CreateTestServer1Config'}
  })

  assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_start_server(test_client: TestClient, db_session: Session, login_user_1: User, should_sync):
  response = test_client.post('/api/server/0/start')
  assert response.status_code == status.HTTP_200_OK
  assert db_session.query(Server).filter_by(id=0).first().enabled

def test_stop_server(test_client: TestClient, db_session: Session, login_user_1: User, should_sync):
  server = db_session.query(Server).filter_by(id=0).first()
  server.status = 'running'
  db_session.commit()

  response = test_client.post('/api/server/0/stop')
  assert response.status_code == status.HTTP_200_OK
  assert not db_session.query(Server).filter_by(id=0).first().enabled

def test_delete_server(test_client: TestClient, db_session: Session, login_user_1: User, should_sync):
  response = test_client.delete('/api/server/0')
  assert response.status_code == status.HTTP_200_OK
  assert db_session.query(Server).filter_by(id=0).first() == None

def test_delete_server_admin_403(test_client: TestClient, login_user_admin: User):
  response = test_client.delete('/api/server/0')
  assert response.status_code == status.HTTP_403_FORBIDDEN

def test_delete_server_super_ok(test_client: TestClient, login_user_super: User, should_sync):
  response = test_client.delete('/api/server/0')
  assert response.status_code == status.HTTP_200_OK

def test_get_server_versions(test_client: TestClient, login_user_1):
  response = test_client.get('/api/server/0/history')
  assert response.json() == [
    {
      'serverId': 0,
      'serverConfig': '{"displayName": "server1Version0"}',
      'numChanges': -1,
      'createdAt': 0,
      'createdBy': 'testuser'
    },
    {
      'serverId': 0,
      'serverConfig': '{"displayName": "server1Version2"}',
      'numChanges': 1,
      'createdAt': 1,
      'createdBy': 'testuser'
    }
  ]

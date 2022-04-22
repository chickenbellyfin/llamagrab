from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy.orm.session import Session

from database.models import Server, ServerVersion, User

def _remove_nones(obj: dict):
  for key in obj.copy():
    if obj[key] is None:
      obj.pop(key)
  return obj

def test_list_servers(test_client: TestClient, db_session: Session, add_servers, server1, logged_in_user):
  db_session.add(logged_in_user)
  db_session.commit()
  response = test_client.get('/api/servers/user')
  assert response.status_code == status.HTTP_200_OK
  assert response.json() == [
    {
      'id': 0,
      'owner': 'testuser',
      'name': 'Test Server 1',
      'region': 'region1',
      'regionName': 'TestRegion1',
      'status': 'stopped',
      'gameMode': 'CTF'
    }
  ]

def test_list_servers_empty(test_client: TestClient, db_session: Session, logged_in_user):
  response = test_client.get('/api/servers/user')
  assert response.status_code == status.HTTP_200_OK
  assert response.json() == []

def test_get_server_settings(test_client: TestClient, db_session: Session, logged_in_user, add_servers):
  response = test_client.get('/api/server/0/settings')  
  assert response.status_code == status.HTTP_200_OK
  assert response.json() == {'region': 'region1'}

def test_get_server_settings_other_user(test_client: TestClient, db_session: Session, logged_in_user, add_servers):
  # server 1 belongs to admin_user
  response = test_client.get('/api/server/1/settings')  
  assert response.status_code == status.HTTP_403_FORBIDDEN

def test_get_server_settings_missing(test_client: TestClient, db_session: Session, logged_in_user):
  response = test_client.get('/api/server/0/settings')  
  assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_server_config(test_client: TestClient, db_session: Session, logged_in_user, add_servers):
  response = test_client.get('/api/server/0/config')  
  assert response.status_code == status.HTTP_200_OK
  assert _remove_nones(response.json()) == {'displayName': 'TestServer1Config'}


def test_set_server_settings(test_client: TestClient, db_session: Session, logged_in_user, add_servers, should_sync):
  response = test_client.post('/api/server/0/settings', json={
    'region': 'region2'
  }) 
  assert response.status_code == status.HTTP_200_OK
  get_response = test_client.get('/api/server/0/settings')  
  assert get_response.status_code == status.HTTP_200_OK
  assert get_response.json() == {'region': 'region2'}


def test_set_server_settings_bad_region(test_client: TestClient, db_session: Session, logged_in_user, add_servers):
  response = test_client.post('/api/server/0/settings', json={
    'region': 'not_a_region'
  }) 
  assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_set_server_config(test_client: TestClient, db_session: Session, logged_in_user, add_servers, should_sync):
  response = test_client.post('/api/server/0/config', json={
    'displayName': 'NewDisplayName'
  }) 
  assert response.status_code == status.HTTP_200_OK
  get_response = test_client.get('/api/server/0/config')  
  assert get_response.status_code == status.HTTP_200_OK
  assert _remove_nones(get_response.json()) == {'displayName': 'NewDisplayName'}
  versions = db_session.query(ServerVersion).filter(ServerVersion.server_id == 0).all()
  assert len(versions) == 3

def test_create_server(test_client: TestClient, db_session: Session, logged_in_user: User, host_manager):
  db_session.add(logged_in_user)
  db_session.commit()
  response = test_client.put('/api/servers', json={
    'serverSettings': { 'region': 'region2' },
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
  assert _remove_nones(get_response.json()) == {'region': 'region2'}

  versions = db_session.query(ServerVersion).filter(ServerVersion.server_id == server_id).all()
  assert len(versions) == 1

def test_create_server_limit(test_client: TestClient, db_session: Session, logged_in_user: User):
  logged_in_user.limits.server_limit = 0
  db_session.add(logged_in_user)
  db_session.commit()
  response = test_client.put('/api/servers', json={
    'serverSettings': { 'region': 'region2' },
    'serverConfig': {'displayName': 'CreateTestServer1Config'}
  })

  assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
  assert response.json() == {'detail': 'Server limit reached for user'}


def test_start_server(test_client: TestClient, db_session: Session, logged_in_user: User, add_servers, should_sync):
  response = test_client.post('/api/server/0/start')
  assert response.status_code == status.HTTP_200_OK
  assert db_session.query(Server).filter_by(id=0).first().status == 'running'


def test_stop_server(test_client: TestClient, db_session: Session, logged_in_user: User, add_servers, should_sync):
  server = db_session.query(Server).filter_by(id=0).first()
  server.status = 'running'
  db_session.commit()

  response = test_client.post('/api/server/0/stop')
  assert response.status_code == status.HTTP_200_OK
  assert db_session.query(Server).filter_by(id=0).first().status == 'stopped'

def test_delete_server(test_client: TestClient, db_session: Session, logged_in_user: User, add_servers, should_sync):
  response = test_client.delete('/api/server/0')
  assert response.status_code == status.HTTP_200_OK
  assert db_session.query(Server).filter_by(id=0).first() == None

def test_delete_server_admin_403(test_client: TestClient, db_session: Session, logged_in_admin: User, add_servers):
  response = test_client.delete('/api/server/0')
  assert response.status_code == status.HTTP_403_FORBIDDEN

def test_delete_server_super_ok(test_client: TestClient, db_session: Session, logged_in_super: User, add_servers, should_sync):
  response = test_client.delete('/api/server/0')
  assert response.status_code == status.HTTP_200_OK

def test_list_all_servers(test_client: TestClient, db_session: Session, add_servers, user, logged_in_admin):
  db_session.add(user)
  db_session.add(logged_in_admin)
  db_session.commit()
  response = test_client.get('/api/servers/all')
  assert response.status_code == status.HTTP_200_OK
  assert response.json() == [
    {
      'id': 0,
      'owner': 'testuser',
      'name': 'Test Server 1',
      'region': 'region1',
      'regionName': 'TestRegion1',
      'status': 'stopped',
      'gameMode': 'CTF'
    },
    {
      'id': 1,
      'owner': 'testadmin',
      'name': 'Test Server 2',
      'region': 'region2',
      'regionName': 'TestRegion2',
      'status': 'stopped',
      'gameMode': 'CTF'
    }
  ]

def test_get_server_versions(test_client: TestClient, add_servers, user, logged_in_admin):
  response = test_client.get('/api/server/0/history')
  assert response.json() == [
    {
      'serverId': 0,
      'serverConfig': 'server1version1',
      'numChanges': -1,
      'createdAt': 0
    },
    {
      'serverId': 0,
      'serverConfig': 'server1version2',
      'numChanges': 1,
      'createdAt': 1
    }
  ]
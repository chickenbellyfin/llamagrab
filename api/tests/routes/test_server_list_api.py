from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm.session import Session
from src.database.models import ServerEditor


def test_list_servers(test_client: TestClient, db_session: Session, server1, login_user_1):
  response = test_client.get('/api/servers/user')
  assert response.status_code == status.HTTP_200_OK
  assert response.json() == [
    {
      'id': 0,
      'owner': 'testuser',
      'name': 'Test Server 1',
      'region': 'region1',
      'regionName': 'TestRegion1',
      'enabled': False,
      'status': 'offline',
      'gameMode': 'CTF',
      'game': 'tribes_ascend_ootb',
      'isPrivate': True
    }
  ]

def test_list_servers_empty(test_client: TestClient, db_session: Session, login_user_2):
  db_session.query(ServerEditor).delete() # clear shared servers
  db_session.commit()
  response = test_client.get('/api/servers/user')
  assert response.status_code == status.HTTP_200_OK
  assert response.json() == []

def test_list_all_servers(test_client: TestClient, login_user_admin):
  response = test_client.get('/api/servers/all')
  assert response.status_code == status.HTTP_200_OK
  assert response.json() == [
    {
      'id': 0,
      'owner': 'testuser',
      'name': 'Test Server 1',
      'region': 'region1',
      'regionName': 'TestRegion1',
      'enabled': False,
      'status': 'offline',
      'gameMode': 'CTF',
      'game': 'tribes_ascend_ootb',
      'isPrivate': True
    },
    {
      'id': 1,
      'owner': 'testadmin',
      'name': 'Test Server 2',
      'region': 'region2',
      'regionName': 'TestRegion2',
      'enabled': False,
      'status': 'offline',
      'gameMode': 'CTF',
      'game': 'tribes_ascend_ootb',
      'isPrivate': False
    }
  ]

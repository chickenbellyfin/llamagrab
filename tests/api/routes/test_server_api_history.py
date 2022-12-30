import json

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm.session import Session

from api.database.models import ServerVersion


def test_get_server_versions(test_client: TestClient, login_user_1):
  response = test_client.get('/api/server/0/history')
  assert response.json() == [
    {
      'versionId': 0,
      'serverId': 0,
      'serverConfig': '{"displayName": "server1Version0"}',
      'numChanges': -1,
      'createdAt': 0,
      'createdBy': 'testuser'
    },
    {
      'versionId': 1,
      'serverId': 0,
      'serverConfig': '{"displayName": "server1Version2"}',
      'numChanges': 1,
      'createdAt': 1,
      'createdBy': 'testuser'
    }
  ]

def test_add_server_versions(test_client: TestClient, login_user_1):
  history_0 = test_client.get('/api/server/0/history')
  assert len(history_0.json()) == 2

  set_response_1 = test_client.post('/api/server/0/config', json={
    'displayName': 'NewDisplayName'
  })

  assert set_response_1.status_code == status.HTTP_200_OK
  history_1 = test_client.get('/api/server/0/history')
  assert len(history_1.json()) == 3

  # setting the config to the same value does not add to history
  set_response_2 = test_client.post('/api/server/0/config', json={
    'displayName': 'NewDisplayName'
  })

  assert set_response_2.status_code == status.HTTP_200_OK
  history_2 = test_client.get('/api/server/0/history')
  assert len(history_2.json()) == 3

def test_server_diff_first(test_client: TestClient, db_session: Session, login_user_1):
  # delete all versions so the version we create will be first
  db_session.query(ServerVersion).delete()
  db_session.commit()

  set_response = test_client.post('/api/server/0/config', json={
    'displayName': 'name1',
    'autoBalance': False,
    "maps": [
      "ctf_katabatic",
      "arena_walledin",
      "ctf_periculo"
    ],
    "admins": [
      "siteuser1",
      "siteuser2"
    ],
    "mediumWeaponBans": [] # changes from [] -> none
  })

  assert set_response.status_code == status.HTTP_200_OK
  version = set_response.json()

  # setting the config to the same value does not add to history
  history_res = test_client.get(f'/api/server/0/history/{version}')

  assert history_res.status_code == status.HTTP_200_OK
  assert history_res.json() == {'changes': []}

def test_server_diff(test_client: TestClient, db_session: Session, login_user_1):
  set_response_1 = test_client.post('/api/server/0/config', json={
    'displayName': 'name1',
    'autoBalance': False,
    "maps": [
      "ctf_katabatic",
      "arena_walledin",
      "ctf_periculo"
    ],
    "admins": [
      "siteuser1",
      "siteuser2"
    ],
    "mediumWeaponBans": [] # changes from [] -> none
  })

  set_response_2 = test_client.post('/api/server/0/config', json={
    'displayName': 'name2',
    'autoBalance': False, # doesn't change
    "maps": [
      "arena_walledin",
      "ctf_periculo",
      "ctf_arx_novena"
    ],
    "admins": [ # only the order changes, no diff
      "siteuser2",
      "siteuser1"
    ],
    "lightWeaponBans": [] # change from none -> []
  })

  assert set_response_1.status_code == status.HTTP_200_OK
  assert set_response_2.status_code == status.HTTP_200_OK
  version = set_response_2.json()

  # setting the config to the same value does not add to history
  history_res = test_client.get(f'/api/server/0/history/{version}')
  assert history_res.status_code == status.HTTP_200_OK
  history = history_res.json()
  assert len(history['changes']) == 2

  expected_changes = set(map(json.dumps, [
    {
      'field': 'maps',
      'old': ['ctf_katabatic'],
      'new': ['ctf_arx_novena']
    },
    {
      'field': 'display_name',
      'old': 'name1',
      'new': 'name2'
    }
  ]))

  assert set(map(json.dumps, history['changes'])) == expected_changes

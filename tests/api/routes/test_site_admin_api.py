from fastapi import status as http_status
from fastapi.testclient import TestClient


def test_get_flags(test_client: TestClient, login_user_admin,):
  response = test_client.get('/api/admin/site/flags')

  assert response.json() == {
    "disable_new_accounts": False,
    "disable_unverified_accounts": False,
    "disable_non_admin_accounts": False,
    "loginserver": None
  }

def test_set_flags(test_client: TestClient, login_user_admin,):
  response1 = test_client.post('/api/admin/site/flag', json={
    'key': 'disable_new_accounts',
    'value': True
  })
  assert response1.status_code == 200

  response2 = test_client.get('/api/admin/site/flags')
  assert response2.json() == {
    "disable_new_accounts": True,
    "disable_unverified_accounts": False,
    "disable_non_admin_accounts": False,
    "loginserver": None
  }

def test_set_flags_wrong_type(test_client: TestClient, login_user_admin,):
  response1 = test_client.post('/api/admin/site/flag', json={
    'key': 'loginserver',
    'value': 5
  })
  assert response1.status_code == http_status.HTTP_400_BAD_REQUEST

  response2 = test_client.post('/api/admin/site/flag', json={
    'key': 'disable_new_accounts',
    'value': "a string"
  })
  assert response2.status_code == http_status.HTTP_400_BAD_REQUEST

  response2 = test_client.get('/api/admin/site/flags')
  assert response2.json() == {
    "disable_new_accounts": False,
    "disable_unverified_accounts": False,
    "disable_non_admin_accounts": False,
    "loginserver": None
  }
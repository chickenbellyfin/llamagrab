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
  assert response1.ok

  response2 = test_client.get('/api/admin/site/flags')
  assert response2.json() == {
    "disable_new_accounts": True,
    "disable_unverified_accounts": False,
    "disable_non_admin_accounts": False,
    "loginserver": None
  }
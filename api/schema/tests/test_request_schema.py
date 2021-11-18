import pytest
from schema.requests import LoginRequest


def mk_login_request(
  username='validusername',
  password='validpassword',
  invite_token=None):
  return LoginRequest.parse_obj({
    'username': username,
    'password': password,
    'invite_token': invite_token
  })

def test_usernames():
  with pytest.raises(ValueError):
    mk_login_request(username='')
  
  # 4 chars
  with pytest.raises(ValueError):
    mk_login_request(username='aaaa')

  # 17 chars
  with pytest.raises(ValueError):
    mk_login_request(username='aaaaaaaaaaaaaaaaa')

  # contains space
  with pytest.raises(ValueError):
    mk_login_request(username='the user')

  # contains newline
  with pytest.raises(ValueError):
    mk_login_request(username='the\nuser')

  # contains dash
  with pytest.raises(ValueError):
    mk_login_request(username='_')

  mk_login_request(username='aA0_z')

def test_password():
  with pytest.raises(ValueError):
    mk_login_request(password='')
  
  with pytest.raises(ValueError):
    mk_login_request(password='$5@!#')
  
  with pytest.raises(ValueError):
    mk_login_request(password='a'*33)



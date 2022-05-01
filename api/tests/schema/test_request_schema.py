import pytest

from src.schema.requests import LoginRequest, SetTribesUsernameRequest


def mk_login_request(
  username='validusername',
  password='validpassword'):
  return LoginRequest.parse_obj({
    'username': username,
    'password': password
  })

def tribes_username(value: str):
  SetTribesUsernameRequest.parse_obj({
    'tribesUsername': value
  })

def test_usernames():
  with pytest.raises(ValueError):
    mk_login_request(username='')
  
  # 4 chars
  with pytest.raises(ValueError):
    mk_login_request(username='aaa')

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

def test_tribes_username():
  with pytest.raises(ValueError):
    tribes_username('a')
  
  with pytest.raises(ValueError):
    tribes_username('aaaaaaaaaaaaaaaa') 

  for c in ['#', '/', ':', '?', '`', '~', '\u0100', '\u0020']:  
    with pytest.raises(ValueError):
      tribes_username('aaaa' + c)
        
  tribes_username('aaaaa') # control
  tribes_username('aaaa\u0021')
  tribes_username('aaaa\u007d')
  


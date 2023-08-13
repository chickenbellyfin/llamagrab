import re
from multiprocessing.sharedctypes import Value


def validate_password(v: str) -> str:
  if v is None or len(v) < 8 or len(v) > 32:
    raise ValueError('Password must be 8-32 characters')
  return v


def check_password(v: str) -> bool:
  try:
    validate_password(v)
    return True
  except:
    return False

def validate_tribes_username(v):
  # length 2-15 chars
  # https://github.com/Griffon26/taserver/blob/master/login_server/player/player.py#L40
  if len(v) < 2 or len(v) > 15:
    raise ValueError('Length must be 2-15 characters')

  # must be ascii encodable
  # https://github.com/Griffon26/taserver/blob/master/login_server/loginserver.py#L175
  try:
    ascii_bytes = v.encode('ascii')
  except UnicodeError:
    raise ValueError('User name contains invalid (i.e. non-ascii) characters')

  # character restrictions
  # https://github.com/Griffon26/taserver/blob/master/common/utils.py#L43
  valid_chars = all((33 <= c <= 126 and chr(c) not in r'#/:?\`~') for c in ascii_bytes)
  if not valid_chars:
    raise ValueError('contains disallowed characters')

  return v

def validate_string(v):
  if v is None:
    return v

  if len(v) > 500:
    raise ValueError('Length must be < 500 characters')

  valid_chars = re.match(r"^[a-zA-Z0-9 _\-\.':/,*\|[\]]*$", v)
  if not valid_chars:
    raise ValueError('contains disallowed characters')

  return v
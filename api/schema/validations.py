

def validate_password(v: str) -> str:
  if len(v) < 8 or len(v) > 32:
    raise ValueError('Password must be 8-32 characters')
  return v
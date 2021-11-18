from typing import Optional
from fastapi_camelcase import CamelModel as BaseModel
from pydantic import validator, ValidationError

from .game_server_config import GameServerConfig
from database import models
import re
from . import validations
from .responses import ServerSettings

class LoginRequest(BaseModel):
  username: str
  password: str

  @validator('username')
  def validate_username(cls, v):
    if len(v) < 5 or len(v) > 16:
      raise ValueError('Username must be 5-16 characters')

    if not re.match('^[a-zA-Z0-9_]+$', v):
      raise ValueError('Username may only contain a-z A-Z 0-9 _')
    return v
  
  @validator('password')
  def validate_password(cls, v: str):
    return validations.validate_password(v)

class AccountCreateRequest(LoginRequest):
  invite_token: str

class UpdatePasswordRequest(BaseModel):
  current_password: str
  new_password: str
  
  @validator('new_password')
  def validate_new_password(cls, v: str) -> str:
    return validations.validate_password(v)
 

class ServerCreateRequest(BaseModel):
  server_settings: ServerSettings
  server_config: GameServerConfig
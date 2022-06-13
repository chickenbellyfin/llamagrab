import re
from typing import List, Optional

from fastapi_camelcase import CamelModel as BaseModel
from pydantic import validator

from . import validations
from .game_server_config import GameServerConfig
from .responses import ServerSettings


class LoginRequest(BaseModel):
  class Config:
    extra='forbid'

  username: str
  password: str


  @validator('username')
  def validate_username(cls, v):
    if len(v) < 4 or len(v) > 16:
      raise ValueError('Username must be 4-16 characters')

    if not re.match('^[a-zA-Z0-9_]+$', v):
      raise ValueError('Username may only contain a-z A-Z 0-9 _')
    return v

  @validator('password')
  def validate_password(cls, v: str):
    return validations.validate_password(v)

class AccountCreateRequest(LoginRequest):
  pass

class SetTribesUsernameRequest(BaseModel):
  class Config:
    extra='forbid'

  tribes_username: str

  @validator('tribes_username')
  def validate_tribes_username(v):
    return validations.validate_tribes_username(v)


class UpdatePasswordRequest(BaseModel):
  current_password: str
  new_password: str

  @validator('new_password')
  def validate_new_password(cls, v: str) -> str:
    return validations.validate_password(v)


class ServerCreateRequest(BaseModel):
  server_settings: ServerSettings
  server_config: GameServerConfig


class ServerSettingsUpdateRequest(BaseModel):
  region: str
  editors: Optional[List[int]]

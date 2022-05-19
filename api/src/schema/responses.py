from typing import Optional, List
from fastapi_camelcase import CamelModel as BaseModel
from .game_server_config import GameServerConfig

class UserLimits(BaseModel):
  server_limit: Optional[int]
  active_limit: Optional[int]
  server_count: int

# User for admin panel user list
class UserAccount(BaseModel):
  id: int
  username: str
  tier: str
  limits: UserLimits
  tribes_username: Optional[str]
  # DO NOT INCLUDE PASSWORD HERE

  class Config:
    orm_mode = True

class User(BaseModel):
  id: int
  username: str

# Used for server list
class ServerStatus(BaseModel):
  id: int
  owner: str # username of the owner
  name: str
  region: Optional[str]
  region_name: Optional[str]
  enabled: bool
  status: str
  game_mode: str
  is_private: bool

  class Config:
    orm_mode = True

# Return editable settings which are not part of the gameserverconfig
class ServerSettings(BaseModel):
  region: Optional[str]
  editors: Optional[List[int]]

  class Config:
    orm_mode = True

class ServerVersion(BaseModel):
  server_id: int
  server_config: str
  num_changes: int
  created_at: int
  created_by: str
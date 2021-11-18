from typing import Optional
from fastapi_camelcase import CamelModel as BaseModel
from .game_server_config import GameServerConfig

class User(BaseModel):
  id: int
  username: str
  server_limit: int
  server_count: int
  role: str
  # DO NOT INCLUDE PASSWORD HERE

  class Config:
    orm_mode = True

# Used for server list
class ServerStatus(BaseModel):
  id: int
  owner: str # username of the owner
  name: str
  region: Optional[str]
  region_name: Optional[str]
  status: str
  game_mode: str

  class Config:
    orm_mode = True

# Return editable settings which are not part of the gameserverconfig
class ServerSettings(BaseModel):
  region: Optional[str]

  class Config:
    orm_mode = True
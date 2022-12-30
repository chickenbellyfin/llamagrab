from typing import List, Optional, Union

from fastapi_camelcase import CamelModel as BaseModel

from api.schema.game_server_config import GameType


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
  game: GameType
  is_private: bool

  class Config:
    orm_mode = True



# Return editable settings which are not part of the gameserverconfig
class ServerSettings(BaseModel):
  region: str
  game: GameType
  editors: Optional[List[int]]

  class Config:
    orm_mode = True

class ServerVersion(BaseModel):
  version_id: int
  server_id: int
  server_config: str
  num_changes: int
  created_at: int
  created_by: str

class ServerVersionChange(BaseModel):
  field: str
  old: Optional[Union[str, List]]
  new: Optional[Union[str, List]]

class ServerVersionDetails(BaseModel):
  changes: List[ServerVersionChange]

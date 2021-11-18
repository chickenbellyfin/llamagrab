from fastapi_camelcase import CamelModel as BaseModel
from typing import List, Optional
import json

class GameServerConfig(BaseModel):
  display_name: str
  description: str
  password: Optional[str] # this is a non-secure game server password
  admin_password: Optional[str]
  
  team_assign_type: str
  auto_balance: bool
  time_limit: int
  overtime_limit: int

  friendly_fire: bool

  maps: List[str]


  def serialize(self):
    return json.dumps(self.dict())

  def parse(json_str: str):
    return GameServerConfig.parse_obj(json.loads(json_str))

  class Config:
    orm_mode = True
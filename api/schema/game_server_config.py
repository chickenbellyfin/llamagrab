from fastapi_camelcase import CamelModel as BaseModel
from typing import List, Optional, Any
import json


class Property(BaseModel):
  name: str
  value: Any

class ItemProperties(BaseModel):
  player_class: str
  weapon: str
  properties: List[Property]

class GameServerConfig(BaseModel):
  display_name: Optional[str]
  description: Optional[str]
  password: Optional[str] # this is a non-secure game server password
  admins: Optional[List[str]]
  
  team_assign_type: Optional[str]
  auto_balance: Optional[bool]
  time_limit: Optional[int]
  overtime_limit: Optional[int]
  warmup_time: Optional[int]
  respawn_time: Optional[int]
  sniper_respawn_delay: Optional[int]
  ammo_pickup_lifespan: Optional[int]
  ctf_flag_timeout: Optional[int]
  max_players: Optional[int]
  naked_spawn: Optional[bool]

  ctf_cap_limit: Optional[int]
  tdm_kill_limit: Optional[int]
  arena_rounds: Optional[int]
  arena_lives: Optional[int]
  rabbit_score_limit: Optional[int]
  cah_score_limit: Optional[int]
  ctf_blitz_all_flags_move: Optional[bool]

  energy_multiplier: Optional[float]
  flag_drag_light: Optional[int]
  flag_drag_medium: Optional[int]
  flag_drag_heavy: Optional[int]
  flag_drag_deceleration: Optional[int]

  friendly_fire_multiplier: Optional[float]
  friendly_fire: Optional[bool]

  map_voting: Optional[bool]
  maps: Optional[List[str]]

  vehicle_health_multiplier: Optional[float]
  grav_cycle_limit: Optional[int]
  grav_cycle_spawn_time: Optional[int]
  shrike_limit: Optional[int]
  shrike_spawn_time: Optional[int]
  beowulf_limit: Optional[int]
  beowulf_spawn_time: Optional[int]

  light_weapon_bans: Optional[List[str]]
  medium_weapon_bans: Optional[List[str]]
  heavy_weapon_bans: Optional[List[str]]

  item_properties: Optional[List[ItemProperties]]


  def serialize(self):
    return json.dumps(self.dict())

  def parse(json_str: str):
    return GameServerConfig.parse_obj(json.loads(json_str))

  class Config:
    orm_mode = True


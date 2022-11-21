import json
from typing import Any, List, Optional

from fastapi_camelcase import CamelModel as BaseModel
from pydantic import validator

from . import validations


class ModProperty(BaseModel):
  name: str
  value: Any

class ItemProperties(BaseModel):
  player_class: str
  weapon: str
  properties: List[ModProperty]

class MutualExclusion(BaseModel):
  player_class: str
  item1: str
  item2: str

class HardcodedLoadout(BaseModel):
  primary: Optional[str]
  secondary: Optional[str]
  tertiary: Optional[str]
  belt: Optional[str]
  pack: Optional[str]

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
  light_count_limit: Optional[int]
  medium_count_limit: Optional[int]
  heavy_count_limit: Optional[int]

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
  light_class_properties: Optional[List[ModProperty]]
  medium_class_properties: Optional[List[ModProperty]]
  heavy_class_properties: Optional[List[ModProperty]]

  force_hardcoded_loadouts: Optional[bool]
  light_hardcoded_loadouts: Optional[List[HardcodedLoadout]]
  medium_hardcoded_loadouts: Optional[List[HardcodedLoadout]]
  heavy_hardcoded_loadouts: Optional[List[HardcodedLoadout]]

  light_disabled_equip_points: Optional[List[str]]
  medium_disabled_equip_points: Optional[List[str]]
  heavy_disabled_equip_points: Optional[List[str]]

  light_value_mods: Optional[List[ModProperty]]
  medium_value_mods: Optional[List[ModProperty]]
  heavy_value_mods: Optional[List[ModProperty]]
  item_value_mods: Optional[List[ItemProperties]]

  mutual_exclusions: Optional[List[MutualExclusion]]

  grav_cycle_properties: Optional[List[ModProperty]]
  shrike_properties: Optional[List[ModProperty]]
  beowulf_properties: Optional[List[ModProperty]]

  @validator('display_name')
  def validate_display_name(cls, v):
    return validations.validate_string(v)

  @validator('description')
  def validate_description(cls, v):
    return validations.validate_string(v)


  def serialize(self):
    return json.dumps(self.dict())

  def parse(json_str: str):
    return GameServerConfig.parse_obj(json.loads(json_str))

  class Config:
    orm_mode = True

import os
from typing import List

from pydantic.main import BaseModel
from schema.game_server_config import GameServerConfig
import json

with open('../common/maps.json') as maps_json:
 maps_raw = json.load(maps_json)
maps = {
  map_obj['key']: map_obj for map_obj in maps_raw
}

with open('../common/weapons.json') as weapons_json:
 weapons_raw = json.load(weapons_json)
weapons = {
  clazz: {
    wep_obj['key']: wep_obj for wep_obj in weapons_raw[clazz]
  } for clazz in weapons_raw
}

team_assign_types = {
  'balanced': 'TeamAssignTypes.Balanced',
  'unbalanced': 'TeamAssignTypes.Unbalanced',
  'auto': 'TeamAssignTypes.AutoAssign'
}

class LuaSettings():
  def __init__(
    self, 
    include_admin = True,
    site_admins: List[str] = [],
    include_hitscan_ban = True
    ):
    self.site_admins = site_admins
    self.include_admin = include_admin
    self.include_hitscan_ban = include_hitscan_ban

class LuaConfig:
  def __init__(self, lua_dir='../common/lua'):
    self.lua = ""
    self.lua_dir = lua_dir

  def __call__(self, template: str, *args) -> None:
      """add a line of lua"""
      # if any args are None, omit the line
      # this makes it easier to define optional config lines
      if len(args) > 0:
        for arg in args:
          if arg is None:
            print(f'for template {template}, arg is None')
            return
      self.lua += (template % args) + '\n'

  def require(self, filename):
    """add a lua file from the common lua lib"""
    with open(os.path.join(self.lua_dir, filename)) as lib:
      lib_str = lib.read()
    self('')
    self(f'-- [{filename}]')
    self('-' * 80)
    self(lib_str)
    self('-' * 80)
  
  def get(self):
    return self.lua

# covert optional bool to lowercase string
def _bool(val):
  return None if val is None else str(val).lower()

def to_lua(config: GameServerConfig, lua_settings: LuaSettings) -> str:
  lua = LuaConfig()

  lua('ServerSettings.Description = "%s"', config.display_name)
  lua('ServerSettings.Motd = "%s"', config.description)

  lua('ServerSettings.GameSettingMode = ServerSettings.GameSettingModes.OOTB')
  lua('ServerSettings.TeamAssignType = %s', team_assign_types.get(config.team_assign_type))
  lua('ServerSettings.MaxPlayers = %s', config.max_players)
  lua('ServerSettings.AutoBalanceTeams = %s', _bool(config.auto_balance))

  lua('ServerSettings.Password = "%s"', config.password)

  lua('ServerSettings.TimeLimit = %d', config.time_limit)
  lua('ServerSettings.OvertimeLimit = %d', config.overtime_limit)
  lua('ServerSettings.WarmupTime = %d', config.warmup_time)
  lua('ServerSettings.RespawnTime = %d', config.respawn_time)
  lua('ServerSettings.SniperRespawnDelay = %d', config.sniper_respawn_delay)
  lua('ServerSettings.AmmoPickupLifespan = %d', config.ammo_pickup_lifespan)
  lua('ServerSettings.CTFFlagTimeout = %d', config.ctf_flag_timeout)

  lua('ServerSettings.FriendlyFire = %s', _bool(config.friendly_fire))
  lua('ServerSettings.FriendlyFireMultiplier = %0.2f', config.friendly_fire_multiplier)
  lua('ServerSettings.NakedSpawn = %s', _bool(config.naked_spawn))

  lua('ServerSettings.VehicleHealthMultiplier = %0.2f', config.vehicle_health_multiplier)
  lua('ServerSettings.GravCycleLimit = %d', config.grav_cycle_limit)
  lua('ServerSettings.GravCycleSpawnTime = %d', config.grav_cycle_spawn_time)

  lua('ServerSettings.ShrikeLimit = %d', config.shrike_limit)
  lua('ServerSettings.ShrikeSpawnTime = %d', config.shrike_spawn_time)

  lua('ServerSettings.BeowulfLimit = %d', config.beowulf_limit)
  lua('ServerSettings.BeowulfSpawnTime = %d', config.beowulf_spawn_time)

  ### Map Rotation  
  lua('ServerSettings.MapRotation.VotingEnabled = %s', _bool(config.map_voting))
  if config.maps:
    for map_key in config.maps:
      map_value = maps[map_key]
      map_lua = map_value['lua']
      if map_value.get('isCustom', False):
        lua('ServerSettings.MapRotation.addCustom("%s")', map_lua)
      else:
        lua('ServerSettings.MapRotation.add(%s)', map_lua)

  # Weapon Bans
  for clazz, ban_list in [
    ('Light', config.light_weapon_bans),
    ('Medium', config.medium_weapon_bans),
    ('Heavy', config.heavy_weapon_bans)
  ]:
    if ban_list:
      for weapon_key in ban_list:
        weapon = weapons[clazz][weapon_key]
        lua('ServerSettings.BannedItems.add("%s", "%s")', clazz, weapon['name'])
  
  if lua_settings.include_hitscan_ban:
    lua.require('hitscan.lua')


  # ### Admin
  if lua_settings.include_admin:
    lua.require('admin.lua')

    for site_admin in lua_settings.site_admins:
      lua('Admin.Roles.addMember("admin", "%s")', site_admin)

    if config.admins:
      for admin in config.admins:
        lua('Admin.Roles.addMember("mod", "%s")', admin)

  return lua.get()

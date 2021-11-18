import os
from schema.game_server_config import GameServerConfig
import json

with open('../common/maps.json') as maps_json:
 maps_raw = json.load(maps_json)

maps = {
  mapv['key']: mapv for mapv in maps_raw
}

team_assign_types = {
  'balanced': 'TeamAssignTypes.Balanced',
  'unbalanced': 'TeamAssignTypes.Unbalanced',
  'auto': 'TeamAssignTypes.AutoAssign'
}

class LuaConfig:
  def __init__(self, lua_dir='../common/lua'):
    self.lua = ""
    self.lua_dir = lua_dir

  def __call__(self, s: str) -> None:
      """add a line of lua"""
      self.lua += f'{s}\n'

  def require(self, filename):
    """add a lua file from the common lua lib"""
    with open(os.path.join(self.lua_dir, filename)) as lib:
      lib_str = lib.read()
    self(lib_str)
  
  def get(self):
    return self.lua

def to_lua(config: GameServerConfig) -> str:
  lua = LuaConfig()

  lua(f'ServerSettings.Description = "{config.display_name}"')
  lua(f'ServerSettings.Motd = "{config.description}"')

  lua(f'ServerSettings.GameSettingMode = ServerSettings.GameSettingModes.OOTB')
  lua(f'ServerSettings.TeamAssignType = {team_assign_types[config.team_assign_type]}')
  lua(f'ServerSettings.AutoBalanceTeams	= {str(config.auto_balance).lower()}')

  if config.password:
    lua(f'ServerSettings.Password = \"{config.password}\"')

  lua(f'ServerSettings.TimeLimit = {config.time_limit}')
  lua(f'ServerSettings.OvertimeLimit = {config.overtime_limit}')
  lua(f'ServerSettings.FriendlyFire = {str(config.friendly_fire).lower()}')

  ### Map Rotation
  for map_key in config.maps:
    map_value = maps[map_key]
    map_lua = map_value['lua']
    if map_value.get('isCustom'):
      lua(f'ServerSettings.MapRotation.addCustom("{map_lua}")')
    else:
      lua(f'ServerSettings.MapRotation.add({map_lua})')

  ### Admin
  lua.require('admin.lua')

  lua('local roles = {')
  lua('{')
  lua('  name = "super",')
  lua(f'  password = "supertest",') # todo inject super password
  lua('  commands = {"NextMap", "NextMapName", "StartMap", "EndMap"},')
  lua('  canLua = true,') # only super can lua
  lua('},')

  if config.admin_password:
    lua('{')
    lua('  name = "admin",')
    lua(f'  password = "{config.admin_password}",')
    lua('  commands = {"NextMap", "NextMapName", "StartMap", "EndMap"},')
    lua('  canLua = false,') # admin (site user) can not lua
    lua('},')
  lua('}')

  lua('doSetupRoles(roles)')

  return lua.get()



if __name__ == '__main__':
  import test_data
  print(to_lua(test_data.servers[1].server_config))
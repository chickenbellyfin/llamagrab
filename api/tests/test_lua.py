from api.lua import LuaSettings, to_lua
from schema.game_server_config import GameServerConfig

TEST_LUA_SETTINGS = LuaSettings(
  include_admin=True,
  site_admins=['siteadmin1', 'siteadmin2']

)

def compare_example(name: str, lua_settings=TEST_LUA_SETTINGS):
  with open(f'tests/examples/{name}.json') as test_in:
    source = GameServerConfig.parse(test_in.read())
  
  with open(f'tests/examples/{name}.lua') as test_out:
    target = test_out.read()
  
  print(to_lua(source, lua_settings))
  assert target == to_lua(source, lua_settings)

def test_empty():
  compare_example('empty', LuaSettings(include_admin=False, include_hitscan_ban=False))

def test_all():
  compare_example('all')
from api.database import models
from api.lua import LuaSettings, to_lua
from api.schema.game_server_config import GameServerConfig

TEST_LUA_SETTINGS = LuaSettings(
  include_admin=True,
  site_admins=['siteadmin1', 'siteadmin2']
)

TEST_SERVER = models.Server(
  id=0,
  user=0,
  name='test_server',
  enabled=True,
  updated_at=0,
  game='tribes_ascend_ootb',
  owner=models.User(
    id=0,
    username='',
    password='',
    tribes_username='test_owner'
  )
)

def compare_example(name: str, server=TEST_SERVER, lua_settings=TEST_LUA_SETTINGS):
  with open(f'tests/api/examples/{name}.json') as test_in:
    source = GameServerConfig.parse(test_in.read())

  with open(f'tests/api/examples/{name}.lua') as test_out:
    target = test_out.read()

  assert target == to_lua(server, source, lua_settings)

def test_empty():
  # server where owner has not set tribes_username
  empty_server = models.Server(
    id=0,
    user=0,
    name='test_server',
    enabled=True,
    updated_at=0,
    game='tribes_ascend_ootb',
    owner=models.User(
      id=0,
      username='',
      password='',
      tribes_username=None
    )
  )
  compare_example('empty', server=empty_server, lua_settings=LuaSettings(include_admin=False, include_hitscan_ban=False))

def test_all():
  compare_example('all')

def test_goty_base():
  goty_server = models.Server(
    id=0,
    user=0,
    name='test_server',
    enabled=True,
    updated_at=0,
    game='tribes_ascend_goty',
    owner=models.User(
      id=0,
      username='',
      password='',
      tribes_username='goty_admin'
    )
  )

  compare_example(
    'goty',
    goty_server,
    LuaSettings(include_admin=False, site_admins=[], include_hitscan_ban=False)
  )

def test_mods_not_admins():
  '''check that site admins dont get set as mods'''
  # server where owner has not set tribes_username
  server = models.Server(
    id=0,
    user=0,
    name='test_server',
    enabled=True,
    updated_at=0,
    game='tribes_ascend_ootb',
    server_config='{"admins": ["siteadmin1"]}',
    owner=models.User(
      id=0,
      username='',
      password='',
      tribes_username=None
    )
  )
  assert 'siteadmin1' in TEST_LUA_SETTINGS.site_admins
  result = to_lua(server, GameServerConfig.parse(server.server_config), TEST_LUA_SETTINGS)
  assert 'addMember("mod", "siteadmin1")' not in result


def test_owner_mod_not_admins():
  '''check that site admins dont get set as mods'''
  # server where owner has not set tribes_username
  server = models.Server(
    id=0,
    user=0,
    name='test_server',
    enabled=True,
    updated_at=0,
    server_config='{}',
    game='tribes_ascend_ootb',
    owner=models.User(
      id=0,
      username='',
      password='',
      tribes_username='siteadmin2'
    )
  )
  assert server.owner.tribes_username in TEST_LUA_SETTINGS.site_admins
  result = to_lua(server, GameServerConfig.parse(server.server_config), TEST_LUA_SETTINGS)
  assert 'addMember("mod", "siteadmin2")' not in result

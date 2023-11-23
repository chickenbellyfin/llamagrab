from typing import Any, Dict

from jinja2_fragments.sanic import render
from loguru import logger
from sanic import HTTPResponse, Request, Sanic
from sanic.request.parameters import RequestParameters
from api.schema import responses

from api.schema.app_config import Region
from api.schema.game_server_config import GameServerConfig
from api.server_status import ServerStatusManager
from api.service.account_service import AccountService
from api.service.server_service import ServerService
from api.views.htmx import if_htmx
from api.views.util import region_statuses
from api import lua


def parse_editor_form_config(form: RequestParameters) -> (dict, dict):
  settings_dict = {}
  config_dict = {}
  for key in form.keys():
    if key.startswith('settings.'):
      settings_dict[key] = form.get(key)
    else:
      config_dict[key] = form.get(key)
  return (settings_dict, config_dict)


def add_views(
  app: Sanic,
  accounts: AccountService,
  servers: ServerService,
  regions: Dict[str, Region],
  status_manager: ServerStatusManager,
  **kwargs
):
  @app.get("/edit_server/<server_id>")
  async def edit_server(request: Request, server_id: int):
    server = servers.get_server(server_id, request.ctx.user)
    editors = servers.get_server_editors(server_id, request.ctx.user)
    config = servers.get_config(server_id, request.ctx.user)
    settings = responses.ServerSettings(
      region=server.region,
      game=server.game,
      editors=[user.id for user in editors]
    )
    return await render(
      "pages/edit_server.html", 
      block=if_htmx('content'),
      context={
        'regions': regions,
        'users': accounts.all(),
        'server': server,
        'config': config,
      }
    )

  @app.post("/edit_server/<server_id>")
  async def update_server(request: Request, server_id: int):
    settings_dict, config_dict = parse_editor_form_config(request.form)
    config = GameServerConfig.parse_obj(config_dict)
    server = servers.get_server(server_id, request.ctx.user)
    lua_str = lua.to_lua(server, config, lua.LuaSettings(include_admin=False, include_hitscan_ban=False))
    print(f'\n---------------------\n{lua_str}')
    return HTTPResponse('')
    
from typing import Dict

from jinja2_fragments.sanic import render
from loguru import logger
from sanic import Request, Sanic
from api.schema import responses

from api.schema.app_config import Region
from api.server_status import ServerStatusManager
from api.service.account_service import AccountService
from api.service.server_service import ServerService
from api.views.htmx import if_htmx
from api.views.util import region_statuses


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
        'config': config,
      }
    )
    
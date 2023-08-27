from typing import Dict

from loguru import logger
from sanic import Request, Sanic

from api.lib.jinja2_fragments import render
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
  @app.get("/create_server")
  async def create_server(request: Request):
    return await render(
      "pages/create_server.html", 
      block=if_htmx('content'),
      context={
        'regions': regions,
        'users': accounts.all()
      }
    )
    
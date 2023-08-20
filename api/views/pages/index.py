from typing import Dict

from loguru import logger
from sanic import Request, Sanic

from api.database.database import Database
from api.lib.jinja2_fragments import render
from api.schema.app_config import Region
from api.server_status import ServerStatusManager
from api.service.server_service import ServerService
from api.views.htmx import if_htmx
from api.views.util import region_statuses, server_status_list


def add_views(
  app: Sanic,
  servers: ServerService,
  database: Database,
  regions: Dict[str, Region],
  status_manager: ServerStatusManager,
  **kwargs
):
  @app.get("/")
  async def get_index(request: Request):
    if not request.ctx.user:
      return await render(
        "pages/landing.html", 
        context={'regions': region_statuses(servers, status_manager, regions, database)}
      )
    else:
      with database.session() as db:
        status_list = server_status_list(
          servers,
          servers.get_owned_servers(request.ctx.user) + servers.get_shared_servers(request.ctx.user)
        )
        
      return await render(
        "pages/home.html",
        context={"servers": status_list},
        block=if_htmx('content')
      )

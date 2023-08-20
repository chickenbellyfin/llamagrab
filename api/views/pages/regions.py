from typing import Dict
from urllib.parse import urlencode

from loguru import logger
from sanic import Request, Sanic, response

from api.database.database import Database
from api.lib.jinja2_fragments import render
from api.schema.app_config import Region
from api.server_status import ServerStatusManager
from api.service.server_service import ServerService
from api.views.htmx import if_htmx, toast
from api.views.util import region_statuses, server_status_list


def add_views(
  app: Sanic,
  servers: ServerService,
  database: Database,
  regions: Dict[str, Region],
  status_manager: ServerStatusManager,
  **kwargs
):
  @app.get("/regions")
  async def get_regions(request: Request):
    return await render(
      "pages/regions.html", 
      block=if_htmx('content'),
      context={'regions': region_statuses(servers, status_manager, regions, database)}
    )
    
from typing import Dict

from jinja2_fragments.sanic import render
from loguru import logger
from sanic import Request, Sanic

from api.schema.app_config import Region
from api.server_status import ServerStatusManager
from api.service.server_service import ServerService
from api.views.htmx import if_htmx
from api.views.util import region_statuses


def add_views(
  app: Sanic,
  servers: ServerService,
  regions: Dict[str, Region],
  status_manager: ServerStatusManager,
  **kwargs
):
  @app.get("/regions")
  async def get_regions(request: Request):
    return await render(
      "pages/regions.html", 
      block=if_htmx('content'),
      context={'regions': region_statuses(servers, status_manager, regions)}
    )
    
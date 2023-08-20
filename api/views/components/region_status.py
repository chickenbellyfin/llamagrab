
from typing import Dict

from sanic import Request, Sanic
from api.database.database import Database
from api.lib.jinja2_fragments import render
from api.schema.app_config import Region

from api.server_status import ServerStatusManager
from api.service.server_service import ServerService
from api.views.util import region_statuses


def add_views(
    app: Sanic, 
    servers: ServerService, 
    status_manager: ServerStatusManager, 
    regions: Dict[str, Region],
    **kwargs
):
      
  @app.get("/components/region_status")
  async def get_region_status(request: Request):
    return await render(
      "components/region_status.html",
      context={'regions': region_statuses(servers, status_manager, regions)}
    )
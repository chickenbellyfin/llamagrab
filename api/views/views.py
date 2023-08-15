from typing import Dict
from sanic import Request, Sanic, response
from api.database import queries
from api.database.database import Database
from api.schema.app_config import Region
from api.schema.game_server_config import GameServerConfig
from api.server_status import ServerStatusManager
from api.service.account_service import AccountService
from api.service.server_service import ServerService
from api.service import exceptions
from api.schema import validations
from api.lib.jinja2_fragments import render
from loguru import logger

from urllib.parse import urlencode

from api.views.util import if_htmx, server_status_list, region_statuses

def query(**kwargs):
   return '?' + urlencode(kwargs) if len(kwargs) else ''

def add_views(
  app: Sanic,
  accounts: AccountService,
  servers: ServerService,
  database: Database,
  regions: Dict[str, Region],
  status_manager: ServerStatusManager,
):
  @app.get("/")
  async def get_index(request: Request):
    if not request.ctx.user:
      return await render(
        "pages/landing.html", 
        context={'regions': region_statuses(status_manager, regions, database)}
      )
    else:
      with database.session() as db:
        status_list = server_status_list(
          servers.get_owned_servers(request.ctx.user) + servers.get_shared_servers(request.ctx.user), 
          status_manager, 
          regions,
          db
        )
        
      return await render(
        "pages/home.html",
        context={"servers": status_list},
        block=if_htmx('content')
      )
  
  @app.get("/regions")
  async def get_regions(request: Request):
    return await render(
      "pages/regions.html", 
      block=if_htmx('content'),
      context={'regions': region_statuses(status_manager, regions, database)}
    )
    
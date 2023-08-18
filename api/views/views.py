from typing import Dict
from urllib.parse import urlencode

from loguru import logger
from sanic import Request, Sanic, response

from api.database.database import Database
from api.lib.jinja2_fragments import render
from api.schema.app_config import Region
from api.server_status import ServerStatusManager
from api.service.account_service import AccountService
from api.service.server_service import ServerService
from api.views.htmx import if_htmx, toast
from api.views.util import region_statuses, server_status_list


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
  
  @app.get("/toast")
  async def get_toast(request: Request):
    res = response.empty()
    import random
    t = random.choice([
      ('success', 'yay!'),
      ('error', 'Oh no!')
    ])
    toast(res, t[0],t[1])
    return res

    
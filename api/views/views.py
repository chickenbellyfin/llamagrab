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
  
  @app.get("/regions")
  async def get_regions(request: Request):
    return await render(
      "pages/regions.html", 
      block=if_htmx('content'),
      context={'regions': region_statuses(servers, status_manager, regions, database)}
    )
  
  @app.get("/region_status")
  async def get_region_status(request: Request):
    return await render(
      "components/region_status.html",
      context={'regions': region_statuses(servers, status_manager, regions, database)}
    )
  
  @app.post('/server/start')
  async def start_server(request: Request):
    server_id = int(request.form.get('id'))
    servers.start_server(server_id, request.ctx.user)
    server = servers.get_server_status(server_id, request.ctx.user)
    res = await render("components/server_card.html", context={'server': server})
    toast(res, message=f'Started {server.name}')
    return res
  
  @app.post('/server/stop')
  async def stop_server(request: Request):
    server_id = int(request.form.get('id'))
    servers.stop_server(server_id, request.ctx.user)
    server = servers.get_server_status(server_id, request.ctx.user)
    res = await render("components/server_card.html", context={'server': server})
    toast(res, message=f'Stopped {server.name}')
    return res
  
  @app.post('/server/restart')
  async def restart_server(request: Request):
    server_id = int(request.form.get('id'))
    servers.restart_server(server_id, request.ctx.user)
    server = servers.get_server_status(server_id, request.ctx.user)
    res = await render("components/server_card.html", context={'server': server})
    toast(res, message=f'Restarting {server.name}')
    return res
    
from typing import Dict
from sanic import Request, Sanic
from sanic_ext import render
from api.database.database import Database
from api.schema.app_config import Region
from api.schema.game_server_config import GameServerConfig
from api.server_status import ServerStatusManager
from api.service.account_service import AccountService
from api.service.server_service import ServerService


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
          return await render("pages/landing.html")
      else:
        with database.session() as db:
          server_list = servers.get_owned_servers(request.ctx.user) + servers.get_shared_servers(request.ctx.user)

        for s in server_list:
          s.region_name = regions[s.region].name if s.region in regions else s.region
          s.status = status_manager.get_server_status(s)
          s.is_private = GameServerConfig.parse(s.server_config).password is not None
        return await render(
          "pages/home.html",
          context={"servers": server_list},
        )
    
    @app.get("/regions")
    async def get_regions(request: Request):
      return await render("pages/regions.html")
    
    @app.get('/settings')
    async def get_settings(request: Request):
       return await render('pages/settings.html')

from typing import Dict
from sanic import Request, Sanic, response
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

from api.views.util import if_htmx

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
          block=if_htmx('content')
        )
    
    @app.get("/regions")
    async def get_regions(request: Request):
      return await render("pages/regions.html", block=if_htmx('content'))
    
    @app.get('/settings')
    async def get_settings(request: Request):
       return await render('pages/settings.html', block=if_htmx('content'))

    @app.post('/set_tribes_username')
    async def post_change_tribes_username(request: Request):
       tribes_username = request.form.get('tribes_username')
       accounts.set_tribes_username(tribes_username, request.ctx.user)
       return await render(
         'pages/settings.html',
         block='tribes_username'
       )
    
    @app.post('/change_password')
    async def post_change_password(request: Request):
      current_password = request.form.get('password')
      new_password = request.form.get('new_password')
      confirm_new_password = request.form.get('confirm_password')

      errors = {}

      if new_password == confirm_new_password:
        try:
          accounts.set_password(new_password, current_password, request.ctx.user)
        except exceptions.UnauthorizedException:
          errors['wrong_password'] = True
        except exceptions.BadArgumentsException:
          errors['invalid_new_password'] = True
      else:
        errors['not_confirmed'] = True
      logger.info(errors)
      return await render(
         'pages/settings.html', 
         block='change_password',
         context={'errors': errors}
      )

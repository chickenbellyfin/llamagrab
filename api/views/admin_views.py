from datetime import datetime
from typing import Dict, List, Union

from dateutil import parser
from loguru import logger
from sanic import Request, Sanic

from api.flags import Flags
from api.audit import AuditLog
from api.database import models
from api.database.database import Database
from api.lib.jinja2_fragments import render
from api.schema.app_config import Loginserver, Region
from api.schema.game_server_config import GameServerConfig
from api.server_status import ServerStatusManager
from api.service.account_service import AccountService
from api.service.server_service import ServerService
from api.views.htmx import if_htmx, toast


def format_date(date: Union[str, datetime]) -> str:
  if type(date) == str:
    date = parser.parse(date)
  return date.strftime("%a %b %d %Y %H:%M:%S %p")


def add_views(
  app: Sanic,
  accounts: AccountService,
  servers: ServerService,
  database: Database,
  regions: Dict[str, Region],
  status_manager: ServerStatusManager,
  audit: AuditLog,
  flags: Flags,
  loginservers: List[Loginserver]
):
  @app.get("/admin/users")
  async def get_users(request: Request):
    all_users = []
    for user in accounts.all():
      user.server_count = len(servers.get_owned_servers(user))
      all_users.append(user)

    return await render(
      "pages/admin/users.html", 
      context={"accounts": all_users},
      block=if_htmx('content')
    )

  @app.get("/admin/servers")
  async def get_servers(request: Request):
    with database.session() as db:
      servers = db.query(models.Server).all()

      for s in servers:
        s.region_name = (
            regions[s.region].name if s.region in regions else s.region
        )
        s.status = status_manager.get_server_status(s)
        s.is_private = (
            GameServerConfig.parse(s.server_config).password is not None
        )

      return await render("pages/admin/servers.html", context={"servers": servers}, block=if_htmx('content'))

  @app.get("/admin/audit")
  async def get_audit_log(request: Request):
    audit_log = audit.get()
    for item in audit_log:
      item.formatted_date = format_date(datetime.fromtimestamp(item.timestamp))
    audit_log.sort(key=lambda i: i.timestamp, reverse=True)
    return await render("pages/admin/audit.html", context={"audit_log": audit_log}, block=if_htmx('content'))

  @app.get("/admin/site")
  async def get_site_settings(request: Request):
    with database.session() as db:
      flag_values = flags.get_all_flags(request.ctx.user)
    return await render(
      "pages/admin/site.html", 
      block=if_htmx('content'),
      context={
        'flags': flag_values,
        'loginservers': loginservers
      }
    )
  
  @app.post('/admin/site/flags')
  async def post_flags(request: Request):
    trigger = request.headers.get('hx-trigger-name')
    logger.info(f'form {request.form} -> {request.form.get(trigger)}')
    if request.form.get(trigger):
      raw_value = request.form.get(trigger)
    else:
      raw_value = None
    logger.info(f't={trigger}, v={raw_value},  f={request.form}')

    success = False

    if trigger in flags.FLAGS:
      flag_type = flags.FLAGS[trigger].flag_type
      if flag_type == bool:
        value = (raw_value != None)
      else: # str
        value = str(raw_value)
    
      try:
        logger.info(f'set_flag({trigger}, {value})')
        flags.set_flag(trigger, value, request.ctx.user)
        success = True
      except Exception as e:
        logger.error(e)

    flag_values = flags.get_all_flags(request.ctx.user)

    res = await render(
      "pages/admin/site.html", 
      block='site_flags',
      context={
        'flags': flag_values,
        'loginservers': loginservers
      }
    )

    toast(
      res, 
      'success' if success else 'error',
      'Flag Updated' if success else 'Failed to update flag'
    )

    return res

  @app.get("/admin/iplogs")
  async def get_iplogs(request: Request):
    return await render("pages/admin/iplogs.html", block=if_htmx('content'))

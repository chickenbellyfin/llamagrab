from typing import Dict, List
from loguru import logger
from sanic import Request, Sanic

from api.audit import AuditLog
from api.database import queries
from api.database.database import Database
from api.flags import Flags
from api.host_manager import HostManager
from api.lib.jinja2_fragments import render
from api.schema.app_config import Loginserver, Region

from api.service.server_service import ServerService
from api.views.htmx import if_htmx, toast


def add_views(
  app: Sanic,
  servers: ServerService,
  database: Database,
  regions: Dict[str, Region],
  host_manager: HostManager,
  audit: AuditLog,
  flags: Flags,
  loginservers: List[Loginserver]
):

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
    if request.form.get(trigger):
      raw_value = request.form.get(trigger)
    else:
      raw_value = None

    success = False

    if trigger in flags.FLAGS:
      flag_type = flags.FLAGS[trigger].flag_type
      if flag_type == bool:
        value = (raw_value != None)
      else: # str
        value = str(raw_value)
    
      try:
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
    toast(res, success, 'Flag Updated' if success else 'Failed to update flag')
    return res
  

  @app.post('/admin/site/request_sync')
  async def post_request_sync(request: Request):
    host_manager.sync()
    audit(request.ctx.user, f'requested a sync')
    
    res = await render("pages/admin/site.html", block='site_actions')
    toast(res, message='Sync Requested')
    return res
  
  @app.post('/admin/site/restart_all')
  async def post_restart_all(request: Request):
    with database.session() as db:
      active = queries.get_active_servers(db)

    host_manager.restart(active)
    audit(request.ctx.user, f'restarted all ({len(active)}) servers')
    
    res = await render("pages/admin/site.html", block='site_actions')
    toast(res, message=f'Restarted {len(active)} servers')
    return res

  @app.post('/admin/site/disable_all')
  async def post_disable_all(request: Request):
    with database.session() as db:
      active = queries.get_active_servers(db)
      for server in active:
        server.enabled = False
      db.commit()

    host_manager.sync()
    audit(request.ctx.user, f'disabled all ({len(active)}) servers')
    
    res = await render("pages/admin/site.html", block='site_actions')
    toast(res, message=f'Disabled {len(active)} servers')
    return res
  

import os
from datetime import datetime
from typing import Dict, List
from httpx import Auth
from sanic import Request, Sanic
import sanic_ext
from collections import namedtuple
from api.audit import AuditLog

from api.database.database import Database
from api.host_manager import HostManager
from api.iplog import IPLogDatabase
from api.schema.app_config import Loginserver, Region
from api.server_status import ServerStatusManager
from api.service.account_service import AccountService
from api.service.server_service import ServerService
from api.views import admin_views, views, test_views, login_views, settings_views
from loguru import logger
from jinja2.runtime import Macro
from common import polling

macro_file_mtimes = {}

def _load_macros_from_file(path, environment):
  with open(path) as f:
    module = environment.from_string(f.read()).module.__dict__
  for key in module:
    if type(module[key]) == Macro:
      logger.info(f'Loaded global macro {key}() from {path}')
      environment.globals[key] = module[key]


def _scan_macros(path, environment):
  for child in os.listdir(path):
    file = os.path.join(path, child)
    if os.path.isfile(file) and file.endswith('.html'):
      mtime = os.path.getmtime(file)
      if macro_file_mtimes.get(file) != mtime:
        _load_macros_from_file(file, environment)
        macro_file_mtimes[file] = mtime
      
def _load_all_jinja_macros(path, environment, poll=False):
  _scan_macros(path, environment)
  if poll:
    def _poll():
      _scan_macros(path, environment)
    polling.fixed_rate(_poll, 1)


def start(
  db_instance: Database,
  auth: Auth,
  host_manager: HostManager,
  status_manager: ServerStatusManager,
  ip_log_db: IPLogDatabase,
  regions: Dict[str, Region],
  loginservers: List[Loginserver],
  audit: AuditLog,
  port=8080,
  secure_cookie=True
):
  servers = ServerService(db_instance, host_manager, status_manager, regions, audit)
  accounts = AccountService(db_instance, auth, servers, host_manager, audit)

  app = Sanic('llamagrab-ssr')
  app.extend(config=sanic_ext.Config(
    templating_path_to_templates='web2/templates',
    templating_enable_async=False
  ))
  app.static('/favicon.ico', 'web2/favicon.ico', name="favicon")
  app.static('/static', 'web2/static', name="static")
  app.ctx.current_year = datetime.now().year # used for page footer

  _load_all_jinja_macros('web2/templates/macros', app.ext.environment, poll=True)

  # make query params available as a dict in request.ctx
  @app.on_request
  async def global_request_context(request: Request):
    request.ctx.query_args = { k: v for k, v in request.query_args }

  login_views.add_views(
    app=app,
    auth=auth,
    accounts=accounts,
    secure_cookie=secure_cookie
  )

  views.add_views(
    app=app,
    accounts=accounts,
    servers=servers,
    database=db_instance,
    regions=regions,
    status_manager=status_manager
  )

  admin_views.add_views(
    app=app,
    accounts=accounts,
    servers=servers,
    database=db_instance,
    regions=regions,
    status_manager=status_manager,
    audit=audit
  )

  settings_views.add_views(
    app=app,
    accounts=accounts
  )

  test_views.add_views(app=app) # TODO remove

  # TODO config to disable single_process (check that host manager etc only runs once)
  # TODO config to set debug=False
  app.run(host="0.0.0.0", port=8080, single_process=True, debug=True, motd=False)

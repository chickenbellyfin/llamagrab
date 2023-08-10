import logging
import os
import sys
from datetime import timedelta
from typing import Dict, List

import uvicorn
import uvicorn.config
import yaml
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_login.fastapi_login import LoginManager
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException

from api import flags, web_app
from api.audit import AuditLog
from api.auth import Auth
from api.database import models, queries
from api.database.database import Database, run_migrations
from api.host_manager import HostManager
from api.iplog import IPLogDatabase
from api.routes import (account_api, admin_api, data_api, ip_log_api,
                        server_api, server_list_api, site_admin_api)
from api.schema.app_config import AppConfig, Loginserver, Region
from api.server_status import ServerStatusManager
from api.service import exceptions
from api.service.account_service import AccountService
from api.service.server_service import ServerService
from common import metrics

DEFAULT_CONFIG_PATH = 'config/config.yaml'

DESCRIPTION = 'API for llamagrab servers. All paths should be prefixed with /api.'
TAGS_METADATA = [
  {
    'name': 'server',
    'description': 'Manage your own servers. Create, edit, start, stop, status.'
  },
  {
    'name': 'server-list',
    'description': 'Fetch lists of servers and their statuses'
  },
  {
    'name': 'account',
    'description': 'User operations, including login.'
  },
  {
    'name': 'data',
    'description': 'Get general info about llamagrab infrastructure.'
  },
]

# https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = sys._getframe(6), 6
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

# https://stackoverflow.com/a/68363904
class SPAStaticFiles(StaticFiles):
  async def get_response(self, path: str, scope):
      is_index = False
      if path == '.' or path == 'index.html':
        is_index = True
      try:
        response = await super().get_response(path, scope)
      except StarletteHTTPException as ex:
        if ex.status_code == 404:
          is_index = True
          response = await super().get_response('.', scope)
        else:
          raise ex

      # for SPAs, index should never be cached
      if is_index:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
      return response


def load_config(argv: List[str]) -> AppConfig:
  config_path = DEFAULT_CONFIG_PATH
  if len(argv) > 1:
    config_path = argv[1]
  
  logger.info(f'Reading config from {config_path}')
  with open(config_path) as config_file:
    config = AppConfig.parse_obj(yaml.safe_load(config_file))
  return config

def create_database(config: AppConfig):
  return Database(config.base_path)


def create_host_manager(config: AppConfig, database: Database) -> HostManager:
  return HostManager(
    regions=config.regions,
    port=int(config.host_manager_port),
    database=database
  )


def create_login_manager(config: AppConfig, database: Database) -> LoginManager:
  # todo get a better login library
  def load_user(username: str) -> models.User:
    with database.session() as db:
      user = queries.get_user(db, username)
      return user

  login_manager = LoginManager(config.login_secret, token_url='/api/login', default_expiry=timedelta(days=30))
  login_manager.user_loader()(load_user)
  return login_manager


def ensure_admin_user(database: Database):
  with database.session() as session:
    admin_user = queries.get_user(session, 'admin')
    if not admin_user:
      logger.info(f'Admin user does not exist, creating')
      # TODO Create only the admin user, add separate script for filling test data
      from api import initialize_db
      initialize_db.populate(session)


def create_app(
  db_instance: Database,
  auth: Auth,
  host_manager: HostManager,
  status_manager: ServerStatusManager,
  ip_log_db: IPLogDatabase,
  regions: Dict[str, Region],
  loginservers: List[Loginserver],
  audit: AuditLog
) -> FastAPI:
  servers = ServerService(db_instance, host_manager, status_manager, regions, audit)
  accounts = AccountService(db_instance, auth, servers, host_manager, audit)
  flags.set_loginserver_urls([s.url for s in loginservers])
  app = FastAPI(
    title="Llamagrab",
    description=DESCRIPTION,
    openapi_tags=TAGS_METADATA,
    redoc_url=None
  )

  account_api.add_routes(
    app=app,
    auth=auth,
    accounts=accounts,
    servers=servers
  )

  admin_api.add_routes(
    app=app,
    auth=auth,
    database=db_instance,
    audit=audit
  )

  data_api.add_routes(
    app=app,
    regions=regions,
    loginservers=loginservers
  )

  server_api.add_routes(
    app=app,
    auth=auth,
    status_manager=status_manager,
    regions=regions,
    servers=servers
  )

  server_list_api.add_routes(
    app=app,
    auth=auth, 
    database=db_instance,
    status_manager=status_manager, 
    regions=regions
  )

  site_admin_api.add_routes(
    app=app,
    auth=auth,
    database=db_instance,
    host_manager=host_manager,
    audit=audit
  )

  ip_log_api.add_routes(
    app=app,
    auth=auth,
    ip_log_db=ip_log_db
  )
  
  app.add_middleware(exceptions.ExceptionHandlerMiddleware)

  return app


def main(argv: List[str]):
  logger.info('Starting API...')

  config = load_config(argv)

  # path for all variable data (db, log, etc)
  base_path = os.path.abspath(config.base_path)
  logger.info(f'base_path={base_path}')

  # uvicorn http logs are filtered out to access.log
  logger.add(os.path.join(base_path, 'app.log'), rotation='10 MB', filter={
    'uvicorn.protocols.http': False
  })
  logger.add(os.path.join(base_path, 'access.log'), rotation='10 MB', filter='uvicorn.protocols.http')
  logger.disable('urllib3')

  db = create_database(config)
  # run DB migrations
  run_migrations(base_path)
  audit = AuditLog(db)
  auth = Auth(
    login_manager=create_login_manager(config, db),
    database=db
  )
  host_manager = create_host_manager(config, db)
  server_status_manager = ServerStatusManager(host_manager)
  ip_log_db = IPLogDatabase(base_path=base_path, host_manager=host_manager, audit=audit)
  # Make sure the admin user exists
  ensure_admin_user(db)

  api = create_app(
    db_instance=db,
    auth=auth,
    host_manager=host_manager,
    status_manager=server_status_manager,
    ip_log_db=ip_log_db,
    regions=config.regions,
    loginservers=config.loginservers,
    audit=audit
  )


  app = FastAPI(docs_url=None, redoc_url=None)
  metrics.expose(app, allowed_ips=config.allowed_metrics_ips)
  app.mount('/api', api)
  # For deployment, the API serve also serves the static web app
  if config.serve_static is not None:
    app.mount('/', SPAStaticFiles(directory=config.serve_static, html=True), name='webapp')

  api.add_middleware(metrics.HTTPMetricsMiddleware, route_prefix='/api')

  # Instead of uvicorn.run, use UvicornBackgroundServer to run non-blocking in a new thread
  # This allows us to start fastapi and sanic, whereas normally they would both block the main thread
  # uvicorn.run(
  #   app,
  #   host='0.0.0.0',
  #   port=config.port,
  #   log_config=None,
  #   proxy_headers=True,
  #   forwarded_allow_ips="*" # allows uvicorn to access log with IPs forwarded by reverse proxy (caddy)
  # )
  from api.uvicorn_background_server import UvicornBackgroundServer
  uvicorn_config = uvicorn.Config(
    app,
    host='0.0.0.0',
    port=config.port,
    log_config=None,
    proxy_headers=True,
    forwarded_allow_ips="*" # allows uvicorn to access log with IPs forwarded by reverse proxy (caddy)
  )
  api_server = UvicornBackgroundServer(config=uvicorn_config)
  api_server.run_nonblocking()

  web_app.start(
    db_instance=db,
    auth=auth,
    host_manager=host_manager,
    status_manager=server_status_manager,
    ip_log_db=ip_log_db,
    regions=config.regions,
    loginservers=config.loginservers,
    audit=audit
  )

  api_server.kill()


if __name__ == '__main__':
  main(sys.argv)

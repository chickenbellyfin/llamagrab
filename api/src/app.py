from datetime import timedelta
import logging
import os
import sys
from typing import List, Mapping
import yaml

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_login import LoginManager
from loguru import logger
import uvicorn
import uvicorn.config


from .host_manager import HostManager
from .database import models, queries
from .database.database import Database, run_migrations
from . import dependencies
from .routes import account_api, admin_api, data_api, server_api, server_list_api
from .server_status import ServerStatusManager


DEFAULT_CONFIG_PATH = 'config.yaml'

# https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

logging.basicConfig(handlers=[InterceptHandler()], level=0)

# https://stackoverflow.com/a/68363904
class SPAStaticFiles(StaticFiles):
  async def get_response(self, path: str, scope):
      response = await super().get_response(path, scope)
      if response.status_code == 404:
          response = await super().get_response('.', scope)
      return response


def load_config(argv: List[str]):
  config_path = DEFAULT_CONFIG_PATH
  if len(argv) > 1:
    config_path = argv[1]

  logger.info(f'Reading config from {config_path}')
  with open(config_path) as config_file:
    config = yaml.safe_load(config_file)

  if not config.get('base_path'):
    config['base_path'] = ''
  return config

def create_database(config):
  return Database(config['base_path'])

def create_host_manager(config, db: Database) -> HostManager:
  return HostManager(
    nodes=config['host_manager']['nodes'],
    port=int(config['host_manager']['port']),
    db_session=db.SessionFactory
  )


def create_login_manager(config, db: Database) -> LoginManager:
  # todo get a better login library
  def load_user(username: str) -> models.User:
    with db.SessionFactory() as db_session:
      user = queries.get_user(db_session, username)
      return user

  login_manager = LoginManager(config['login_secret'], token_url='/api/login', default_expiry=timedelta(days=1))
  login_manager.user_loader()(load_user)
  return login_manager


def ensure_admin_user(db: Database):
  with db.SessionFactory() as session:
    admin_user = queries.get_user(session, 'admin')
    if not admin_user:
      logger.info(f'Admin user does not exist, creating')
      # TODO Create only the admin user, add separate script for filling test data
      from src import dummy_data
      dummy_data.populate(session)


def create_app(
  db_instance: Database,
  login_manager: LoginManager,
  host_manager: HostManager,
  status_manager: ServerStatusManager,
  regions: Mapping[str, str]
) -> FastAPI:

  dependencies.dependencies.set(
    db_session=db_instance.SessionFactory,
    login_manager=login_manager,
    host_manager=host_manager,
    status_manager=status_manager,
    regions=regions
  )
  app = FastAPI()
  app.include_router(account_api.router)
  app.include_router(admin_api.router)
  app.include_router(data_api.router)
  app.include_router(server_api.router)
  app.include_router(server_list_api.router)

  return app


def main(argv: List[str]):
  logger.info('Starting API...')

  config = load_config(argv)

  # path for all variable data (db, log, etc)
  base_path = os.path.abspath(config.get('base_path', ''))
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

  login_manager = create_login_manager(config, db)
  host_manager = create_host_manager(config, db)
  server_status_manager = ServerStatusManager(
    host_manager,
    polling_rate=config.get('status_polling_rate_secs', 60)
  )

  # Make sure the admin user exists
  ensure_admin_user(db)

  api = create_app(
    db_instance=db,
    login_manager=login_manager,
    host_manager=host_manager,
    status_manager=server_status_manager,
    regions=config['regions']
  )

  app = FastAPI()
  app.mount('/api', api)
  # For deployment, the API serve also serves the static web app
  if config.get('serve_static'):
    app.mount('/', SPAStaticFiles(directory=config['serve_static'], html=True), name='webapp')

  uvicorn.run(
    app,
    host='0.0.0.0',
    port=config.get('port', 8000),
    debug=True,
    log_config=None,
    proxy_headers=True
  )


if __name__ == '__main__':
  main(sys.argv)
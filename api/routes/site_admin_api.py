
from fastapi import Depends, FastAPI
from fastapi import status as http_status
from fastapi.exceptions import HTTPException
from loguru import logger
from sqlalchemy.orm.session import Session

from api import flags
from api.audit import AuditLog
from api.auth import Auth
from api.database import models, queries
from api.database.database import Database
from api.host_manager import HostManager
from api.schema.requests import SetFlagRequest


def add_routes(
  app: FastAPI,
  auth: Auth,
  database: Database,
  host_manager: HostManager,
  audit: AuditLog
):
  @app.post('/admin/site/flag', include_in_schema=False)
  async def set_flag(request: SetFlagRequest, user: models.User = Depends(auth.login_admin), db: Session = Depends(database)):
    logger.info(
      f"User(id={user.id} username={user.username}) Set Flag {request.key} = {request.value} ({type(request.value)})")
    try:
      flag = flags.set_flag(db, request.key, request.value)
      audit(user, f'updated {flag}')
    except TypeError:
      raise HTTPException(http_status.HTTP_400_BAD_REQUEST)

  @app.get('/admin/site/flags', include_in_schema=False)
  async def get_flags(user: models.User = Depends(auth.login_admin), db: Session = Depends(database)):
    return flags.get_all_flags(db)

  @app.post('/admin/site/request_sync', include_in_schema=False)
  async def request_sync(user: models.User = Depends(auth.login_admin)):
    logger.info(f"User(id={user.id}, username={user.username}) requested sync")
    host_manager.sync()
    audit(user, f'requested a sync')

  @app.post('/admin/site/restart_all', include_in_schema=False)
  async def restart_all(user: models.User = Depends(auth.login_admin), db: Session = Depends(database)):
    active = queries.get_active_servers(db)
    logger.info(f"{user} restarted all servers")
    host_manager.restart(active)
    audit(user, f'restarted all ({len(active)}) servers')
    return len(active)

  @app.post('/admin/site/restart_all/{region}', include_in_schema=False)
  async def restart_all(region: str, user: models.User = Depends(auth.login_admin), db: Session = Depends(database)):
    active = queries.get_active_servers(db, region = region)
    logger.info(f"{user} restarted all servers in {region}")
    host_manager.restart(active)    
    audit(user, f'restarted all ({len(active)}) servers in {region}')
    return len(active)

  @app.post('/admin/site/disable_all', include_in_schema=False)
  async def disable_all(user: models.User = Depends(auth.login_admin), db: Session = Depends(database)):
    active = queries.get_active_servers(db)
    logger.info(f"{user} disabled all servers")
    for server in active:
      server.enabled = False
    db.commit()
    host_manager.sync()    
    audit(user, f'disabled all ({len(active)}) servers')
    return len(active)

  @app.post('/admin/site/disable_all/{region}', include_in_schema=False)
  async def disable_all(region: str, user: models.User = Depends(auth.login_admin), db: Session = Depends(database)):
    active = queries.get_active_servers(db, region = region)
    logger.info(f"{user} disabled all servers in {region}")
    for server in active:
      server.enabled = False
    db.commit()
    host_manager.sync()
    audit(user, f'disabled all ({len(active)}) servers in {region}')
    return len(active)

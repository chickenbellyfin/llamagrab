
from fastapi import Depends
from fastapi import status as http_status
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from loguru import logger
from sqlalchemy.orm.session import Session

from api import flags
from api.auth import Auth
from api.database import models, queries
from api.database.database import Database
from api.host_manager import HostManager
from api.schema.requests import SetFlagRequest


def build_router(
  auth: Auth,
  database: Database,
  host_manager: HostManager
) -> APIRouter:
  router = APIRouter()

  @router.post('/admin/site/flag', include_in_schema=False)
  async def set_flag(request: SetFlagRequest, user: models.User = Depends(auth.login_admin), db: Session = Depends(database)):
    logger.info(
      f"User(id={user.id} username={user.username}) Set Flag {request.key} = {request.value} ({type(request.value)})")
    try:
      flags.set_flag(db, request.key, request.value)
    except TypeError:
      raise HTTPException(http_status.HTTP_400_BAD_REQUEST)

  @router.get('/admin/site/flags', include_in_schema=False)
  async def get_flags(user: models.User = Depends(auth.login_admin), db: Session = Depends(database)):
    return flags.get_all_flags(db)

  @router.post('/admin/site/request_sync', include_in_schema=False)
  async def request_sync(user: models.User = Depends(auth.login_admin)):
    logger.info(f"User(id={user.id}, username={user.username}) requested sync")
    host_manager.sync()

  @router.post('/admin/site/restart_all', include_in_schema=False)
  async def restart_all(user: models.User = Depends(auth.login_admin), db: Session = Depends(database)):
    active = queries.get_active_servers(db)
    logger.info(f"User(id={user.id}, username={user.username}) restarted all servers")
    host_manager.restart(active)
    return len(active)

  @router.post('/admin/site/restart_all/{region}', include_in_schema=False)
  async def restart_all(region: str, user: models.User = Depends(auth.login_admin), db: Session = Depends(database)):
    active = queries.get_active_servers(db, region = region)
    logger.info(f"User(id={user.id}, username={user.username}) restarted all servers in {region}")
    host_manager.restart(active)
    return len(active)

  @router.post('/admin/site/disable_all', include_in_schema=False)
  async def disable_all(user: models.User = Depends(auth.login_admin), db: Session = Depends(database)):
    active = queries.get_active_servers(db)
    logger.info(f"User(id={user.id}, username={user.username}) disabled all servers")
    for server in active:
      server.enabled = False
    db.commit()
    host_manager.sync()
    return len(active)

  @router.post('/admin/site/disable_all/{region}', include_in_schema=False)
  async def disable_all(region: str, user: models.User = Depends(auth.login_admin), db: Session = Depends(database)):
    active = queries.get_active_servers(db, region = region)
    logger.info(f"User(id={user.id}, username={user.username}) disabled all servers in {region}")
    for server in active:
      server.enabled = False
    db.commit()
    host_manager.sync()
    return len(active)
  
  return router


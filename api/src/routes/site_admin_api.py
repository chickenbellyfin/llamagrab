
from fastapi.routing import APIRouter
from fastapi import Depends
from loguru import logger
from src.schema.requests import SetFlagRequest

from sqlalchemy.orm.session import Session

from src.database import models, queries

from src.dependencies import dependencies as deps
from src import flags

router = APIRouter()


@router.post('/admin/site/flag', include_in_schema=False)
async def set_flag(request: SetFlagRequest, user: models.User = Depends(deps.login_admin), db: Session = Depends(deps.db)):
  logger.info(
    f"Set Flag {request.key} = {request.value} ({type(request.value)})")
  flags.set_flag(db, request.key, request.value)


@router.get('/admin/site/flags', include_in_schema=False)
async def get_flags(user: models.User = Depends(deps.login_admin), db: Session = Depends(deps.db)):
  return flags.get_all_flags(db)


@router.post('/admin/site/request_sync', include_in_schema=False)
async def request_sync(user: models.User = Depends(deps.login_admin)):
  logger.info(f"User(id={user.id}, username={user.username}) requested sync")
  deps.host_manager().sync()

@router.post('/admin/site/restart_all', include_in_schema=False)
async def request_sync(user: models.User = Depends(deps.login_admin), db: Session = Depends(deps.db)):
  active = queries.get_active_servers(db)
  logger.info(f"User(id={user.id}, username={user.username}) restarted all servers")
  for server in active:
    deps.status_manager.notify_restarting(server)
    deps.host_manager().restart(server)
  return len(active)

@router.post('/admin/site/disable_all', include_in_schema=False)
async def request_sync(user: models.User = Depends(deps.login_admin), db: Session = Depends(deps.db)):
  active = queries.get_active_servers(db)
  logger.info(f"User(id={user.id}, username={user.username}) disabled all servers")
  for server in active:
    server.enabled = False
    deps.status_manager.notify_disabled(server)
  db.commit()
  deps.host_manager().sync()
  return len(active)


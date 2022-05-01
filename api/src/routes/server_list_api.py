
from typing import List

from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm.session import Session

from src.database import models, queries as db_queries
from src.dependencies import dependencies as deps
from src.schema import responses
from src import server_sharing

router = APIRouter()


def server_status_list(servers: List[models.Server], db: Session) -> List[responses.ServerStatus]:
  return [
    responses.ServerStatus(
      id=s.id,
      owner=db_queries.user_by_id(db, s.user).username,
      name=s.name,
      region=s.region,
      region_name=deps.regions.get(s.region, s.region),
      status=s.status,
      game_mode=s.game_mode
    )
    for s in servers
  ]

@router.get('/servers/user')
async def get_servers_for_user(
  user: models.User = Depends(deps.login),
  db: Session = Depends(deps.db)
):
  """
  Get all servers which the requesting user owns or is an editor of
  """
  servers = db_queries.get_servers(db, user)  
  shared_servers = server_sharing.get_shared_servers(db, user)
  return server_status_list(servers + shared_servers, db)

@router.get('/servers/all')
async def get_all_servers_for_admin(
  admin: models.User = Depends(deps.login_admin),
  db: Session = Depends(deps.db)
):
  """Get all servers for admin panel
  """
  servers = db.query(models.Server).all()
  return server_status_list(servers, db)


@router.get('/servers/active')
async def get_all_active_servers():
  """
  Get all currently running servers for status page
  """
  pass

from typing import List

from fastapi import Depends
from fastapi.routing import APIRouter
from sqlalchemy.orm.session import Session

from api import server_sharing
from api.database import models, queries
from api.dependencies import dependencies as deps
from api.schema import responses
from api.schema.game_server_config import GameServerConfig

router = APIRouter()


def server_status_list(servers: List[models.Server], db: Session) -> List[responses.ServerStatus]:
  return [
    responses.ServerStatus(
      id=s.id,
      owner=queries.user_by_id(db, s.user).username,
      name=s.name,
      region=s.region,
      region_name=deps.regions[s.region].name if s.region in deps.regions else s.region,
      enabled=s.enabled,
      status=deps.status_manager.get_server_status(s),
      game=s.game,
      is_private=GameServerConfig.parse(s.server_config).password is not None
    )
    for s in servers
  ]

@router.get('/servers/user', tags=['server-list'])
async def get_servers_for_user(
  user: models.User = Depends(deps.login),
  db: Session = Depends(deps.db)
):
  """
  Get all servers which the requesting user owns or is an editor of
  """
  servers = queries.get_servers(db, user)
  shared_servers = server_sharing.get_shared_servers(db, user)
  return server_status_list(servers + shared_servers, db)

@router.get('/servers/all', include_in_schema=False)
async def get_all_servers_for_admin(
  admin: models.User = Depends(deps.login_admin),
  db: Session = Depends(deps.db)
):
  """Get all servers for admin panel
  """
  servers = db.query(models.Server).all()
  return server_status_list(servers, db)


@router.get('/servers/region_status', tags=['server-list'])
async def get_region_status(
  db: Session = Depends(deps.db)
):
  """
  Get all currently running servers for status page
  """
  region_status = [
    {
      'region': region.name,
      'online': deps.status_manager.get_region_status(region.key),
      'servers': server_status_list(queries.get_active_servers(db, region.key), db)
    }
    for region in deps.regions.values()
  ]
  return region_status

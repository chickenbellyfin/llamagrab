"""
/api/server[s]/*
Methods for managing servers & server configs
Endpoints in the Server API require user authentication.
"""
import time

from fastapi import Depends
from fastapi import status as http_status
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.orm.session import Session

from api import permissions, server_history, server_sharing
from api.database import models
from api.database import queries as db_queries
from api.dependencies import dependencies as deps
from api.schema import requests, responses
from api.schema.game_server_config import GameServerConfig
from api.schema.responses import ServerVersionChange, ServerVersionDetails

router = APIRouter()

def get_server(
  server_id: int,
  user: models.User = Depends(deps.login),
  db: Session = Depends(deps.db)) -> models.Server:
  """
  Dependency function to get the server from server_id
  Raises 403 if the server does not belong to the requesting user
  Raises 404 if the server does not exist
  """
  server = db_queries.get_server(db, server_id)
  if server is None:
    raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND)
  elif not permissions.can_read_server(db, user, server):
    raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN)

  return server

@router.put('/servers', status_code=http_status.HTTP_201_CREATED, tags=['server'])
async def create_server(
  request: requests.ServerCreateRequest,
  user: models.User = Depends(deps.login),
  db: Session = Depends(deps.db)):
  """ Create a new server"""

  if not permissions.can_create_server(db, user):
    raise HTTPException(status_code=http_status.HTTP_429_TOO_MANY_REQUESTS, detail="Server limit reached for user")

  now = int(time.time())
  new_server = models.Server(
    user=user.id,
    region=request.server_settings.region,
    name=request.server_config.display_name,
    game=request.server_settings.game,
    server_config=request.server_config.serialize(),
    updated_at=now,
    updated_by=user.id
  )

  db.add(new_server)
  db.commit()
  server_sharing.set_server_editors(db, new_server, request.server_settings.editors or [])
  server_history.add_version(db, new_server)

  return responses.ServerStatus(
    id=new_server.id,
    owner=user.username,
    name=new_server.name,
    region=new_server.region,
    enabled=new_server.enabled,
    status='offline', # new server is offline
    game=new_server.game,
    is_private=request.server_config.password is not None
  )

@router.get('/server/{server_id}/status', tags=['server'])
async def get_server_status(server: models.Server = Depends(get_server)):
  """ Get the current status of a server"""
  config = GameServerConfig.parse(server.server_config)
  return responses.ServerStatus(
    id=server.id,
    owner=server.owner.username,
    name=server.name,
    region=server.region,
    region_name=deps.regions[server.region].name if server.region in deps.regions else server.region,
    enabled=server.enabled,
    status=deps.status_manager.get_server_status(server),
    game=server.game,
    is_private=config.password is not None
  )

@router.get('/server/{server_id}/settings', tags=['server'])
async def get_server_settings(
  server: models.Server = Depends(get_server),
  db: Session = Depends(deps.db)
):
  """ Get the settings for a server. These are high-level/infrastructure related settings.
      See /server/{server_id}/config for game settings
  """
  editors = server_sharing.get_server_editors(db, server)
  return responses.ServerSettings(
    region=server.region,
    game=server.game,
    editors=[user.id for user in editors]
  )

@router.post('/server/{server_id}/settings', tags=['server'])
async def set_server_settings(
  request: requests.ServerSettingsUpdateRequest,
  user: models.User = Depends(deps.login),
  server: models.Server = Depends(get_server),
  db: Session = Depends(deps.db)
):
  """ Set the settings for a server. These are high-level/infrastructure related settings.
      See /server/{server_id}/config for game settings
  """
  if not permissions.can_write_server(db, user, server):
    raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN)

  # if editors was modified, check that the user has permission to share the server
  editors_changed = set(server_sharing.get_server_editors(db, server)) != set(request.editors or [])
  if editors_changed and not permissions.can_share_server(user, server):
    raise HTTPException(
      status_code=http_status.HTTP_403_FORBIDDEN,
      detail='User cannot modify editors of server'
    )

  if request.region not in deps.regions:
    raise HTTPException(
      status_code=http_status.HTTP_400_BAD_REQUEST,
      detail='Region does not exist'
    )

  server_sharing.set_server_editors(db, server, request.editors or [])
  server.region = request.region
  db.commit()
  deps.host_manager().sync()

@router.get('/server/{server_id}/config', tags=['server'])
async def get_server_config(server: models.Server = Depends(get_server)) -> GameServerConfig:
  """ Get the game server configuration (Tribes settings) for a server"""
  return GameServerConfig.parse(server.server_config)

@router.post('/server/{server_id}/config', tags=['server'])
async def set_server_config(
  game_server_config: GameServerConfig,
  user: models.User = Depends(deps.login),
  server: models.Server = Depends(get_server),
  db: Session = Depends(deps.db)):
  """ Set the game server configuration (Tribes settings) for a server"""
  if not permissions.can_write_server(db, user, server):
    raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN)

  server.name = game_server_config.display_name
  server.server_config = game_server_config.serialize()
  server.updated_at = int(time.time())
  server.updated_by = user.id
  db.commit()

  server_history.add_version(db, server)

  deps.host_manager().sync()


@router.post('/server/{server_id}/start', tags=['server'])
async def start_server( server: models.Server = Depends(get_server), db: Session = Depends(deps.db)):
  """ Request to start a server. Status will be enabled=True immediatley, but the server may not be started immediatley.
      You should poll /api/server/{server_id}/status status to wait for the server to actually start."""
  server.enabled = True
  db.commit()
  deps.host_manager().sync()


@router.post('/server/{server_id}/stop', tags=['server'])
async def stop_server(server: models.Server = Depends(get_server), db: Session = Depends(deps.db)):
  """ Request to stop a server. Status will be enabled=False immediatley, but the server may not stop immediately.
      You should poll /api/server/{server_id}/status status to wait for the server to actually stop."""
  server.enabled = False
  db.commit()
  deps.host_manager().sync()

@router.post('/server/{server_id}/restart', tags=['server'])
async def restart_server(server: models.Server = Depends(get_server), db: Session = Depends(deps.db)):
  """ Restart a server. Server will be restart immediately on the host. If the server is already restarting, will
  return an error."""
  if deps.status_manager.get_server_status(server) != 'running':
    raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST)

  deps.host_manager().restart(server)

@router.delete('/server/{server_id}', tags=['server'])
async def delete_server(
  user: models.User = Depends(deps.login),
  server: models.Server = Depends(get_server),
  db: Session = Depends(deps.db)
):
  if server.user != user.id and user.tier != 'super':
    raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN)

  versions = server_history.get_versions(db, server)
  for version in versions:
    db.delete(version)
  db.query(models.ServerEditor).filter(models.ServerEditor.server_id == server.id).delete()
  db.delete(server)
  db.commit()
  deps.host_manager().sync()


@router.get('/server/{server_id}/history', tags=['server'])
async def get_server_history(
  user: models.User = Depends(deps.login),
  server: models.Server = Depends(get_server),
  db: Session = Depends(deps.db)
):
  """ Get all past versions of a server's settings"""
  return [
    responses.ServerVersion(
      version_id=s.id,
      server_id=s.server_id,
      server_config=s.server_config,
      num_changes=s.num_changes,
      created_at=s.created_at,
      created_by=s.creator.username if s.creator else 'deleted user'
    ) for s in server_history.get_versions(db, server)
  ]

@router.get('/server/{server_id}/history/{id}')
async def get_server_version_diff(
  id: int,
  server: models.Server = Depends(get_server),
  db: Session = Depends(deps.db)
) -> ServerVersionDetails:
  diff = server_history.get_diff(db, server, id)

  return ServerVersionDetails(
    changes=[
      ServerVersionChange(field=k, old=v['old'], new=v['new'])
      for k, v in diff.items()
    ]
  )

"""
/api/server[s]/*
Methods for managing servers & server configs
Endpoints in the Server API require user authentication.
"""
import time
from typing import List

from fastapi import Depends, status as http_status
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.orm.session import Session

from src.database import models, queries as db_queries
from src.dependencies import dependencies as deps
from src.schema import requests, responses
from src.schema.game_server_config import GameServerConfig
from src import  permissions, server_history, server_sharing

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

@router.put('/servers', status_code=http_status.HTTP_201_CREATED)
async def create_server(
  request: requests.ServerCreateRequest,
  user: models.User = Depends(deps.login),
  db: Session = Depends(deps.db)):

  if not permissions.can_create_server(db, user):
    raise HTTPException(status_code=http_status.HTTP_429_TOO_MANY_REQUESTS, detail="Server limit reached for user")

  now = int(time.time())
  new_server = models.Server(
    user=user.id,
    region=request.server_settings.region,
    name=request.server_config.display_name,
    game_mode='Custom',
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
    status=new_server.status,
    game_mode=new_server.game_mode,
    is_private=request.server_config.password is not None
  )

@router.get('/server/{server_id}/status')
async def get_server_status(server: models.Server = Depends(get_server)):
  config = GameServerConfig.parse(server.server_config)
  return responses.ServerStatus(
    id=server.id,
    owner=server.owner.username,
    name=server.name,
    region=server.region,
    status=server.status,
    game_mode=server.game_mode,
    is_private=config.password is not None
  )

@router.get('/server/{server_id}/settings')
async def get_server_settings(
  server: models.Server = Depends(get_server),
  db: Session = Depends(deps.db)
):
  editors = server_sharing.get_server_editors(db, server)
  return responses.ServerSettings(
    region=server.region,
    editors=[user.id for user in editors]
  )

@router.post('/server/{server_id}/settings')
async def set_server_settings(
  request: responses.ServerSettings,
  user: models.User = Depends(deps.login),
  server: models.Server = Depends(get_server),
  db: Session = Depends(deps.db)
):
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

@router.get('/server/{server_id}/config')
async def get_server_config(server: models.Server = Depends(get_server)) -> GameServerConfig:
  return responses.GameServerConfig.parse(server.server_config)

@router.post('/server/{server_id}/config')
async def set_server_config(
  game_server_config: GameServerConfig,
  user: models.User = Depends(deps.login),
  server: models.Server = Depends(get_server),
  db: Session = Depends(deps.db)):

  if not permissions.can_write_server(db, user, server):
    raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN)

  server.name = game_server_config.display_name
  server.server_config = game_server_config.serialize()
  server.updated_at = int(time.time())
  db.commit()

  server_history.add_version(db, server)

  deps.host_manager().sync()


@router.post('/server/{server_id}/start')
async def start_server( server: models.Server = Depends(get_server), db: Session = Depends(deps.db)):
  server.status = 'running'
  db.commit()
  deps.host_manager().sync()


@router.post('/server/{server_id}/stop')
async def stop_server(server: models.Server = Depends(get_server), db: Session = Depends(deps.db)):
  server.status = 'stopped'
  db.commit()
  deps.host_manager().sync()

@router.delete('/server/{server_id}')
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


@router.get('/server/{server_id}/history')
async def get_server_history(
  user: models.User = Depends(deps.login),
  server: models.Server = Depends(get_server),
  db: Session = Depends(deps.db)
):
  return [
    responses.ServerVersion(
      server_id=s.server_id,
      server_config=s.server_config,
      num_changes=s.num_changes,
      created_at=s.created_at,
      created_by=s.creator.username if s.creator else 'deleted user'
    ) for s in server_history.get_versions(db, server)
  ]

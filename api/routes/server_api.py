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

from starlette.responses import PlainTextResponse
from lua import LuaSettings
from lua import to_lua
import database.queries as db_queries
from database import models
from schema import requests, responses
from schema.game_server_config import GameServerConfig, diff_game_server_config
from dependencies import dependencies as deps
from loguru import logger
import permissions

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
  elif server.user != user.id and not permissions.is_admin(user):
    raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN)
  
  return server


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
async def list_servers(
  user: models.User = Depends(deps.login),
  db: Session = Depends(deps.db)
):
  servers = db_queries.get_servers(db, user)
  return server_status_list(servers, db)

@router.get('/server/{server_id}/settings')
async def get_server_settings(
  server: models.Server = Depends(get_server)
):
  return responses.ServerSettings(
    region=server.region
  )

@router.post('/server/{server_id}/settings')
async def set_server_settings(
  request: responses.ServerSettings,
  server: models.Server = Depends(get_server),
  db: Session = Depends(deps.db)
):
  if request.region not in deps.regions:
    raise HTTPException(
      status_code=http_status.HTTP_400_BAD_REQUEST,
      detail='Region does not exist'
    )
  server.region = request.region
  db.commit()
  deps.host_manager().sync()

@router.put('/servers', status_code=http_status.HTTP_201_CREATED)
async def create_server(
  request: requests.ServerCreateRequest,
  user: models.User = Depends(deps.login),
  db: Session = Depends(deps.db)):
  
  if not permissions.can_create_server(db, user):
    raise HTTPException(
      status_code=http_status.HTTP_429_TOO_MANY_REQUESTS,
      detail="Server limit reached for user")
  else:
    now = int(time.time())
    new_server = models.Server(
      user=user.id,
      region=request.server_settings.region,
      name=request.server_config.display_name,
      game_mode='Custom',
      server_config=request.server_config.serialize(),
      updated_at=now
    )

    db.add(new_server)
    db.commit()

    history_entry = models.ServerVersion(
      server_id = new_server.id,
      server_config = new_server.server_config,
      num_changes = -1,
      created_at = new_server.updated_at
    )
    db.add(history_entry)
    db.commit()

    return responses.ServerStatus(
      id=new_server.id,
      owner=user.username,
      name=new_server.name,
      region=new_server.region,
      status=new_server.status,
      game_mode=new_server.game_mode
    )

@router.get('/server/{server_id}/config')
async def get_server_config(server: models.Server = Depends(get_server)) -> GameServerConfig:
  return responses.GameServerConfig.parse(server.server_config)


@router.post('/server/{server_id}/config')
async def set_server_config(
  game_server_config: GameServerConfig,
  server: models.Server = Depends(get_server),
  db: Session = Depends(deps.db)):

  now = int(time.time())
  config_diff = diff_game_server_config(
    GameServerConfig.parse(server.server_config), # old
    game_server_config # new
  )

  history_entry = models.ServerVersion(
    server_id = server.id,
    server_config = game_server_config.serialize(),
    num_changes = len(config_diff.keys()),
    created_at = now
  )

  db.add(history_entry)

  server.name = game_server_config.display_name
  server.server_config = game_server_config.serialize()
  server.updated_at = now

  db.commit()
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
async def delete_server(user: models.User = Depends(deps.login), server: models.Server = Depends(get_server), db: Session = Depends(deps.db)):

  if server.user != user.id and user.tier != 'super':
    raise HTTPException(
      status_code=http_status.HTTP_403_FORBIDDEN
    )

  versions = db_queries.get_server_versions(db, server.id)
  for version in versions:
    db.delete(version)
  db.delete(server)
  db.commit()
  deps.host_manager().sync()


@router.get('/server/{server_id}/history')
async def get_server_history(user: models.User = Depends(deps.login), server: models.Server = Depends(get_server), db: Session = Depends(deps.db)):
  history = db_queries.get_server_versions(db, server.id)
  return [
    responses.ServerVersion(
      server_id=s.server_id,
      server_config=s.server_config,
      num_changes=s.num_changes,
      created_at=s.created_at
    ) for s in history
  ]


@router.get('/servers/all')
async def list_servers_all(admin: models.User = Depends(deps.login_admin), db: Session = Depends(deps.db)):
  servers = db.query(models.Server).all()
  return server_status_list(servers, db)


# TODO
# users should get cleaned-up lua without admin settings/passwords
# @router.get('/server/{server_id}/lua', response_class=PlainTextResponse)
# async def get_server_lua(server: models.Server = Depends(get_server), db: Session = Depends(deps.db)):
#   lua_settings = LuaSettings(include_admin=True, site_admins=db_queries.get_admin_tribes_usernames(db))
#   return to_lua(GameServerConfig.parse(server.server_config), lua_settings)
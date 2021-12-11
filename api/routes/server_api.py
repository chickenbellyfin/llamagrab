"""
/api/server[s]/*
Methods for managing servers & server configs
Endpoints in the Server API require user authentication.
"""
from typing import List
from fastapi import Depends, status as http_status
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.orm.session import Session
import os

from starlette.responses import PlainTextResponse, Response
from lua import LuaSettings
from lua import to_lua
import database.queries as db_queries
from database import models
from schema import requests, responses
from schema.game_server_config import GameServerConfig
from dependencies import dependencies as deps
import time
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
  deps.server_manager().sync()

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
    new_server = models.Server(
      user=user.id,
      region=request.server_settings.region,
      name=request.server_config.display_name,
      game_mode='Custom',
      server_config=request.server_config.serialize()
    )
    db.add(new_server)
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

  server.name = game_server_config.display_name
  server.server_config = game_server_config.serialize()
  db.commit()
  deps.server_manager().sync()


@router.post('/server/{server_id}/start')
async def start_server( server: models.Server = Depends(get_server), db: Session = Depends(deps.db)):
  server.status = 'running'
  db.commit()
  deps.server_manager().sync()


@router.post('/server/{server_id}/stop')
async def stop_server(server: models.Server = Depends(get_server), db: Session = Depends(deps.db)):
  server.status = 'stopped'
  db.commit()
  deps.server_manager().sync()

@router.delete('/server/{server_id}')
async def delete_server(user: models.User = Depends(deps.login_super), server: models.Server = Depends(get_server), db: Session = Depends(deps.db)):
  db.delete(server)
  db.commit()
  deps.server_manager().sync()


@router.get('/servers/all')
async def list_servers_all(admin: models.User = Depends(deps.login_admin), db: Session = Depends(deps.db)):
  servers = db.query(models.Server).all()
  return server_status_list(servers, db)


# TODO
# users should get cleaned-up lua without admin settings/passwords
@router.get('/server/{server_id}/lua', response_class=PlainTextResponse)
async def get_server_lua(server: models.Server = Depends(get_server), db: Session = Depends(deps.db)):
  lua_settings = LuaSettings(include_admin=True, site_admins=db_queries.get_admin_tribes_usernames(db))
  return to_lua(GameServerConfig.parse(server.server_config), lua_settings)
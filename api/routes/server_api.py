"""
/api/server[s]/*
Methods for managing servers & server configs
Endpoints in the Server API require user authentication.
"""
from typing import Dict

from fastapi import Depends, FastAPI
from fastapi import status as http_status

from api.auth import Auth
from api.database import models
from api.schema import requests, responses
from api.schema.app_config import Region
from api.schema.game_server_config import GameServerConfig
from api.schema.responses import ServerVersionChange, ServerVersionDetails
from api.server_status import ServerStatusManager
from api.service.server_service import ServerService


def add_routes(
  app: FastAPI,
  auth: Auth,
  status_manager: ServerStatusManager,
  regions: Dict[str, Region],
  servers: ServerService
):


  @app.put('/servers', status_code=http_status.HTTP_201_CREATED, tags=['server'])
  async def create_server(
    request: requests.ServerCreateRequest,
    user: models.User = Depends(auth.login)):
    """ Create a new server"""
    new_server = servers.create_server(
      region=request.server_settings.region,
      editors=request.server_settings.editors,
      game=request.server_settings.game,
      config=request.server_config,
      user=user
    )

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

  @app.get('/server/{server_id}/status', tags=['server'])
  async def get_server_status(server_id: int, user: models.User = Depends(auth.login)):
    """ Get the current status of a server"""
    server = servers.get_server(server_id, user)
    config = GameServerConfig.parse(server.server_config)
    status = status_manager.get_server_status(server)

    return responses.ServerStatus(
      id=server.id,
      owner=server.owner.username,
      name=server.name,
      region=server.region,
      region_name=regions[server.region].name if server.region in regions else server.region,
      enabled=server.enabled,
      status=status,
      game=server.game,
      is_private=config.password is not None
    )

  @app.get('/server/{server_id}/settings', tags=['server'])
  async def get_server_settings(server_id: int, user: models.User = Depends(auth.login)):
    """ Get the settings for a server. These are high-level/infrastructure related settings.
        See /server/{server_id}/config for game settings
    """
    server = servers.get_server(server_id, user)
    editors = servers.get_server_editors(server_id, user)
    return responses.ServerSettings(
      region=server.region,
      game=server.game,
      editors=[user.id for user in editors]
    )

  @app.post('/server/{server_id}/settings', tags=['server'])
  async def set_server_settings(
    server_id: int,
    request: requests.ServerSettingsUpdateRequest,
    user: models.User = Depends(auth.login)
  ):
    """ Set the settings for a server. These are high-level/infrastructure related settings.
        See /server/{server_id}/config for game settings
    """
    servers.update_settings(server_id, request.region, request.editors, user)

  @app.get('/server/{server_id}/config', tags=['server'])
  async def get_server_config(server_id: int, user: models.User = Depends(auth.login)) -> GameServerConfig:
    """ Get the game server configuration (Tribes settings) for a server"""
    return servers.get_config(server_id, user)

  @app.post('/server/{server_id}/config', tags=['server'])
  async def set_server_config(
    server_id: int,
    game_server_config: GameServerConfig,
    user: models.User = Depends(auth.login)
  ):
    """ Set the game server configuration (Tribes settings) for a server
        Returns the new current version id (or the previous version id if there are no changes)
    """
    version = servers.set_config(server_id, game_server_config, user)
    return version


  @app.post('/server/{server_id}/start', tags=['server'])
  async def start_server( server_id: int, user: models.User = Depends(auth.login)):
    """ Request to start a server. Status will be enabled=True immediatley, but the server may not be started immediatley.
        You should poll /api/server/{server_id}/status status to wait for the server to actually start."""
    servers.start_server(server_id, user)


  @app.post('/server/{server_id}/stop', tags=['server'])
  async def stop_server(server_id: int, user: models.User = Depends(auth.login)):
    """ Request to stop a server. Status will be enabled=False immediatley, but the server may not stop immediately.
        You should poll /api/server/{server_id}/status status to wait for the server to actually stop."""
    servers.stop_server(server_id, user)

  @app.post('/server/{server_id}/restart', tags=['server'])
  async def restart_server(server_id: int, user: models.User = Depends(auth.login)):
    """ Restart a server. Server will be restart immediately on the host. If the server is already restarting, will
    return an error."""
    servers.restart_server(server_id, user)

  @app.delete('/server/{server_id}', tags=['server'])
  async def delete_server(server_id: int, user: models.User = Depends(auth.login)):
    servers.delete_server(server_id, user)

  @app.get('/server/{server_id}/history', tags=['server'])
  async def get_server_history(server_id: int, user: models.User = Depends(auth.login)):
    """ Get all past versions of a server's settings"""
    versions = servers.get_versions(server_id, user)
    return [
      responses.ServerVersion(
        version_id=s.id,
        server_id=s.server_id,
        server_config=s.server_config,
        num_changes=s.num_changes,
        created_at=s.created_at,
        created_by=s.creator.username if s.creator else 'deleted user'
      ) for s in versions
    ]

  @app.get('/server/{server_id}/history/{version_id}')
  async def get_server_version_diff(server_id: int, version_id: int, user: models.User = Depends(auth.login)) -> ServerVersionDetails:
    diff = servers.get_diff(server_id, version_id, user)
    return ServerVersionDetails(
      changes=[
        ServerVersionChange(field=k, old=v['old'], new=v['new'])
        for k, v in diff.items()
      ]
    )

from datetime import datetime
from typing import Dict, Union
from dateutil import parser

from sanic import Request

from api import permissions
from api.database import models
from api.schema.app_config import Region
from api.server_status import ServerStatusManager
from api.service import exceptions
from api.service.server_service import ServerService


def format_date(timestamp: int) -> str:
  return datetime.fromtimestamp(timestamp).strftime("%a %b %d %Y %H:%M:%S %p")

def region_statuses(
    servers: ServerService,
    status_manager: ServerStatusManager,
    regions: Dict[str, Region]
):
    return [{
      'region_name': region.name,
      'online': status_manager.get_region_status(region.key),
      'servers': servers.get_server_status(servers.get_active_servers(region.key))
    } for region in regions.values()
    ]

def _check_user(user: models.User, permissions_func):
    if not user:
       raise exceptions.UnauthorizedException()
    if not permissions_func(user):
       raise exceptions.PermissionsException()

def requires_login(func):
  async def wrapped(request: Request):
    _check_user(request.ctx.user, permissions.is_any)
    return await func(request)
  return wrapped

def requires_admin(func):
  async def wrapped(request: Request):
    _check_user(request.ctx.user, permissions.is_admin)
    return await func(request)
  return wrapped
  
def requires_super(func):
  async def wrapped(request: Request):
    _check_user(request.ctx.user, permissions.is_super)
    return await func(request)
  return wrapped
   
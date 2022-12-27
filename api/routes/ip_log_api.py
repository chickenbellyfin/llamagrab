
from typing import Optional
from fastapi import Depends, HTTPException

from fastapi import status as http_status
from fastapi.routing import APIRouter
from loguru import logger

from api.auth import Auth
from api.database import models
from api.iplog import IPLogDatabase
from fastapi_camelcase import CamelModel as BaseModel
from ipaddress import ip_network


class IPBanRequest(BaseModel):
  ip: str
  reason: Optional[str]

def build_router(
  auth: Auth,
  ip_log_db: IPLogDatabase
) -> APIRouter:
  router = APIRouter()

  @router.get('/admin/ip/log', include_in_schema=False)
  async def get_log(user: models.User = Depends(auth.login_super)):
    entries = ip_log_db.get()
    entries.sort(key=lambda t: t.timestamp, reverse=True)
    return entries

  @router.post('/admin/ip/fetch', include_in_schema=False)
  async def fetch(user: models.User = Depends(auth.login_super)):
    ip_log_db._poll()

  @router.get('/admin/ip/bans', include_in_schema=False)
  async def get_bans():
    return sorted(ip_log_db.get_bans(), key=lambda t: t.created_at, reverse=True)

  @router.post('/admin/ip/ban', include_in_schema=False)
  async def create_ban(ban: IPBanRequest, user: models.User = Depends(auth.login_super)):
    try:
      network = ip_network(ban.ip)
      
      if network.prefixlen < 8:
        raise ValueError('netmask can not be < 8 bits')
      if not network.is_global:
        raise ValueError('IP must be public')
    except ValueError as e:
      raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))
    logger.info(f'Creating IP Ban for ip={ban.ip} and reason="{ban.reason}" by {user.id}')
    ip_log_db.create_ban(ban.ip, user.username, ban.reason)

  @router.delete('/admin/ip/ban/{id}', include_in_schema=False)
  async def remove_ban(id: int, user: models.User = Depends(auth.login_super)):
    ip_log_db.remove_ban(id)
  
  @router.post('/admin/ip/push_banlist', include_in_schema=False)
  async def push_banlist(user: models.User = Depends(auth.login_admin)):
    ip_log_db.push_banlist()

  return router

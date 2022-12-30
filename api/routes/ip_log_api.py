
from ipaddress import ip_network
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi import status as http_status
from fastapi_camelcase import CamelModel as BaseModel
from loguru import logger

from api.audit import AuditLog
from api.auth import Auth
from api.database import models
from api.iplog import IPLogDatabase


class IPBanRequest(BaseModel):
  ip: str
  reason: Optional[str]

def add_routes(
  app: FastAPI,
  auth: Auth,
  ip_log_db: IPLogDatabase,
  audit: AuditLog
):

  @app.get('/admin/ip/log', include_in_schema=False)
  async def get_log(user: models.User = Depends(auth.login_admin)):
    entries = ip_log_db.get()
    entries.sort(key=lambda t: t.timestamp, reverse=True)
    return entries

  @app.post('/admin/ip/fetch', include_in_schema=False)
  async def fetch(user: models.User = Depends(auth.login_admin)):
    ip_log_db._poll()

  @app.get('/admin/ip/bans', include_in_schema=False)
  async def get_bans():
    return sorted(ip_log_db.get_bans(), key=lambda t: t.created_at, reverse=True)

  @app.post('/admin/ip/ban', include_in_schema=False)
  async def create_ban(ban: IPBanRequest, user: models.User = Depends(auth.login_admin)):
    try:
      network = ip_network(ban.ip)
      
      if network.prefixlen < 8:
        raise ValueError('netmask can not be < 8 bits')
      if not network.is_global:
        raise ValueError('IP must be public')
    except ValueError as e:
      raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))
    logger.info(f'Creating IP Ban for ip={ban.ip} and reason="{ban.reason}" by {user.id}')
    created = ip_log_db.create_ban(ban.ip, user.username, ban.reason)
    if created is not None:
      audit(user, f'created {created}')

  @app.delete('/admin/ip/ban/{id}', include_in_schema=False)
  async def remove_ban(id: int, user: models.User = Depends(auth.login_admin)):
    deleted = ip_log_db.remove_ban(id)
    audit(user, f'deleted {deleted}')
  
  @app.post('/admin/ip/push_banlist', include_in_schema=False)
  async def push_banlist(user: models.User = Depends(auth.login_admin)):
    ip_log_db.push_banlist()
    audit(user, 'triggered IP banlist push')

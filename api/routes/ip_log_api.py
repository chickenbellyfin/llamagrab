from fastapi import Depends, FastAPI
from fastapi_camelcase import CamelModel as BaseModel
from loguru import logger

from api.auth import Auth
from api.database import models
from api.iplog import IPLogDatabase


class IPBanRequest(BaseModel):
  ip: str
  reason: str

def add_routes(
  app: FastAPI,
  auth: Auth,
  ip_log_db: IPLogDatabase
):

  @app.get('/admin/ip/log', include_in_schema=False)
  async def get_log(user: models.User = Depends(auth.login_admin)):
    entries = ip_log_db.get(user)
    entries.sort(key=lambda t: t.timestamp, reverse=True)
    return entries

  @app.post('/admin/ip/fetch', include_in_schema=False)
  async def fetch(user: models.User = Depends(auth.login_admin)):
    ip_log_db.do_poll(user)

  @app.get('/admin/ip/bans', include_in_schema=False)
  async def get_bans(user: models.User = Depends(auth.login_admin)):
    return sorted(ip_log_db.get_bans(user), key=lambda t: t.created_at, reverse=True)

  @app.post('/admin/ip/ban', include_in_schema=False)
  async def create_ban(ban: IPBanRequest, user: models.User = Depends(auth.login_admin)):
    logger.info(f'Creating IP Ban for ip={ban.ip} and reason="{ban.reason}" by {user.id}')
    ip_log_db.create_ban(ban.ip, ban.reason, user)

  @app.delete('/admin/ip/ban/{id}', include_in_schema=False)
  async def remove_ban(id: int, user: models.User = Depends(auth.login_admin)):
    ip_log_db.remove_ban(id, user)
  
  @app.post('/admin/ip/push_banlist', include_in_schema=False)
  async def push_banlist(user: models.User = Depends(auth.login_admin)):
    ip_log_db.push_banlist()

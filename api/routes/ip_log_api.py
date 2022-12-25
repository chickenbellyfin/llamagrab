
from fastapi import Depends
from fastapi.routing import APIRouter
from loguru import logger

from api.database import models
from api.dependencies import Dependencies
from api.iplog import IPLogDatabase



def build_router(
  deps: Dependencies,
  ip_log_db: IPLogDatabase
) -> APIRouter:
  router = APIRouter()

  @router.get('/admin/ip/log', include_in_schema=False)
  async def get_log(user: models.User = Depends(deps.login_super)):
    entries = ip_log_db.get()
    entries.sort(key=lambda t: t.timestamp, reverse=True)
    return entries

  @router.post('/admin/ip/fetch', include_in_schema=False)
  async def fetch(user: models.User = Depends(deps.login_super)):
    ip_log_db._poll()
  
  return router

from fastapi import Depends
from fastapi.routing import APIRouter
from loguru import logger

from api.database import models
from api.dependencies import dependencies as deps

router = APIRouter()


@router.get('/admin/ip/log', include_in_schema=False)
async def get_log(user: models.User = Depends(deps.login_super)):
  entries = deps.ip_log_db.get()
  entries.sort(key=lambda t: t.timestamp, reverse=True)
  return entries

@router.post('/admin/ip/fetch', include_in_schema=False)
async def fetch(user: models.User = Depends(deps.login_super)):
  deps.ip_log_db._poll()
"""
/api/admin/*
All endpoints in under the Admin API require the authenticated user to have a role of 'admin' or higher
"""

from fastapi import Depends, Response, status as http_status
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.orm.session import Session
import os
from database import models
from dependencies import dependencies as deps
import time
from loguru import logger


TOKEN_TTL_SECS = 60 * 60 * 24 # 1 day

router = APIRouter()

@router.post('/admin/invite')
async def create_invite(
  user: models.User = Depends(deps.login),
  db: Session = Depends(deps.db)):
  if user.role != 'admin':
    raise HTTPException(status_code=http_status.HTTP_403_FORBIDDEN)
  
  invite_token = os.urandom(32).hex()
  logger.info(f'creating new invite token {invite_token} requested by {user.username}')

  new_invite = models.Invite(
   token=invite_token,
   expires_at=int(time.time() + TOKEN_TTL_SECS),
   created_by=user.id
  )

  db.add(new_invite)
  db.commit()
  
  return {
    "invite_token": invite_token
  }
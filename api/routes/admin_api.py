"""
/api/admin/*
All endpoints in under the Admin API require the authenticated user to have a role of 'admin' or higher
"""

from fastapi import Depends
from fastapi import status as http_status
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from loguru import logger
from sqlalchemy.orm.session import Session

from api import permissions
from api.database import models
from api.dependencies import dependencies as deps

TOKEN_TTL_SECS = 60 * 60 * 24 # 1 day

router = APIRouter()

@router.post('/admin/verify_user/{id_to_verify}', include_in_schema=False)
async def verify_user(id_to_verify: int, user: models.User = Depends(deps.login_admin), db: Session = Depends(deps.db)):
  user_to_verify = db.query(models.User).filter_by(id=id_to_verify).first()
  if not user_to_verify:
    raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND)

  if permissions.is_verified(user_to_verify):
    raise HTTPException(
      status_code=http_status.HTTP_400_BAD_REQUEST,
      detail='User is already verified'
    )

  logger.info(f'User {user_to_verify.id} was verified by {user.id}')
  user_to_verify.tier = 'verified'
  user_to_verify.limits.server_limit = 5
  user_to_verify.limits.active_limit = 2
  db.commit()

@router.post('/admin/make_admin/{id_to_admin}', include_in_schema=False)
async def make_admin(id_to_admin: int, user: models.User = Depends(deps.login_super), db: Session = Depends(deps.db)):
  user_to_admin = db.query(models.User).filter_by(id=id_to_admin).first()
  if not user_to_admin:
    raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND)

  if permissions.is_admin(user_to_admin):
    raise HTTPException(
      status_code=http_status.HTTP_400_BAD_REQUEST,
      detail='User is already admin'
    )

  logger.info(f'User {id_to_admin} was made admin by {user.id}')
  user_to_admin.tier = 'admin'
  user_to_admin.limits.server_limit = None
  user_to_admin.limits.active_limit = None
  db.commit()


@router.delete('/admin/make_admin/{id_to_unadmin}', include_in_schema=False)
async def make_admin(id_to_unadmin: int, user: models.User = Depends(deps.login_super), db: Session = Depends(deps.db)):
  user_to_unadmin = db.query(models.User).filter_by(id=id_to_unadmin).first()
  if not user_to_unadmin:
    raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND)

  if not permissions.is_admin(user_to_unadmin):
    raise HTTPException(
      status_code=http_status.HTTP_400_BAD_REQUEST,
      detail='User is not an admin'
    )

  logger.info(f'User {id_to_unadmin} was made non-admin by {user.id}')
  user_to_unadmin.tier = 'verified'
  user_to_unadmin.limits.server_limit = 5
  user_to_unadmin.limits.active_limit = 2
  db.commit()

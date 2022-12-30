"""
/api/admin/*
All endpoints in under the Admin API require the authenticated user to have a role of 'admin' or higher
"""

from fastapi import Depends, FastAPI
from fastapi import status as http_status
from fastapi.exceptions import HTTPException
from loguru import logger
from sqlalchemy.orm.session import Session

from api import permissions
from api.audit import AuditLog
from api.auth import Auth
from api.database import models
from api.database.database import Database


def add_routes(
  app: FastAPI,
  auth: Auth,
  database: Database,
  audit: AuditLog
):

  @app.post('/admin/verify_user/{id_to_verify}', include_in_schema=False)
  async def verify_user(id_to_verify: int, user: models.User = Depends(auth.login_admin), db: Session = Depends(database)):
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
    audit(user, f'updated {user_to_verify}\'s tier from unverified to verified')

  @app.post('/admin/make_admin/{id_to_admin}', include_in_schema=False)
  async def make_admin(id_to_admin: int, user: models.User = Depends(auth.login_super), db: Session = Depends(database)):
    user_to_admin = db.query(models.User).filter_by(id=id_to_admin).first()
    if not user_to_admin:
      raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND)

    if permissions.is_admin(user_to_admin):
      raise HTTPException(
        status_code=http_status.HTTP_400_BAD_REQUEST,
        detail='User is already admin'
      )

    logger.info(f'User {id_to_admin} was made admin by {user.id}')
    old_tier = user_to_admin.tier
    user_to_admin.tier = 'admin'
    user_to_admin.limits.server_limit = None
    user_to_admin.limits.active_limit = None
    db.commit()
    audit(user, f'updated {user_to_admin}\'s tier from {old_tier} to admin')


  @app.delete('/admin/make_admin/{id_to_unadmin}', include_in_schema=False)
  async def make_admin(id_to_unadmin: int, user: models.User = Depends(auth.login_super), db: Session = Depends(database)):
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
    audit(user, f'updated {user_to_unadmin}\'s tier from admin to verified')
  
  @app.get('/admin/audit_log', include_in_schema=False)
  async def get_audit_log(user: models.User = Depends(auth.login_admin)):
    return sorted(audit.get(), key=lambda t: t.timestamp, reverse=True)


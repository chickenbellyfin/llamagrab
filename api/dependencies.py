from typing import List

from fastapi import Request, status
from fastapi.exceptions import HTTPException
from fastapi.security.oauth2 import SecurityScopes
from fastapi_login.fastapi_login import LoginManager
from sqlalchemy.orm.session import Session, sessionmaker

from api import flags, permissions
from api.database.models import User


class Dependencies:
  def __init__(
    self,
    db_session: sessionmaker ,
    login_manager: LoginManager,
  ): 
    self._db_session = db_session
    self.login_manager = login_manager
    # set of IPs which created an account
    self.created_account = set()

  def db(self) -> Session:
    session: Session = self._db_session()
    try:
      yield session
    finally:
      session.close()

  def check_account_disabled_flags(self, user: User):
    with self._db_session() as db:
      if not permissions.is_verified(user) and flags.get_flag(db, 'disable_unverified_accounts'):
        raise HTTPException(status.HTTP_403_FORBIDDEN)
      elif not permissions.is_admin(user) and flags.get_flag(db, 'disable_non_admin_accounts'):
        raise HTTPException(status.HTTP_403_FORBIDDEN)


  async def login(self, request: Request, security_scopes: SecurityScopes = None) -> User:
    user = await self.login_manager(request, security_scopes)
    self.check_account_disabled_flags(user)
    return user

  async def login_admin(self, request: Request, security_scopes: SecurityScopes = None) -> User:
    user = await self.login_manager(request, security_scopes)
    self.check_account_disabled_flags(user)
    if not permissions.is_admin(user):
      raise HTTPException(status.HTTP_403_FORBIDDEN)
    return user

  async def login_super(self, request: Request, security_scopes: SecurityScopes = None) -> User:
    user = await self.login_manager(request, security_scopes)
    self.check_account_disabled_flags(user)
    if not permissions.is_super(user):
      raise HTTPException(status.HTTP_403_FORBIDDEN)
    return user

from datetime import timedelta

from fastapi import Request, status
from fastapi.exceptions import HTTPException
from fastapi.security.oauth2 import SecurityScopes
from fastapi_login.fastapi_login import LoginManager

from api import flags, permissions
from api.database.database import Database
from api.database.models import User


class Auth:
  def __init__(
    self,
    login_manager: LoginManager,
    database: Database,
  ): 
    self._database = database
    self.login_manager = login_manager


  def check_account_disabled_flags(self, user: User):
    with self._database.session() as session:
      if not permissions.is_verified(user) and flags.get_flag(session, 'disable_unverified_accounts'):
        raise HTTPException(status.HTTP_403_FORBIDDEN)
      elif not permissions.is_admin(user) and flags.get_flag(session, 'disable_non_admin_accounts'):
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

from typing import Dict

from fastapi import Request, status
from fastapi.exceptions import HTTPException
from fastapi.params import Depends
from fastapi.security.oauth2 import SecurityScopes
from fastapi_login.fastapi_login import LoginManager
from sqlalchemy.orm.session import Session, sessionmaker

from . import permissions
from .database.models import User
from .host_manager import HostManager
from .server_status import ServerStatusManager


class Dependencies:
  def __init__(self):
    self._db_session = None
    self.login_manager = None

  def set(self,
    db_session: sessionmaker ,
    login_manager: LoginManager,
    host_manager: HostManager,
    status_manager: ServerStatusManager,
    regions: Dict[str, str]):
    self._db_session = db_session
    self.login_manager = login_manager
    self._host_manager = host_manager
    self.status_manager = status_manager
    self.regions = regions

    # set of IPs which created an account
    self.created_account = set()

  def db(self) -> Session:
    session: Session = self._db_session()
    try:
      yield session
    finally:
      session.close()

  def host_manager(self) -> HostManager:
    return self._host_manager

  async def login(self, request: Request, security_scopes: SecurityScopes = None) -> User:
    return await self.login_manager(request, security_scopes)

  async def login_admin(self, request: Request, security_scopes: SecurityScopes = None) -> User:
    user = await self.login_manager(request, security_scopes)
    if not permissions.is_admin(user):
      raise HTTPException(status.HTTP_403_FORBIDDEN)
    return user

  async def login_super(self, request: Request, security_scopes: SecurityScopes = None) -> User:
    user = await self.login_manager(request, security_scopes)
    if not permissions.is_super(user):
      raise HTTPException(status.HTTP_403_FORBIDDEN)
    return user

dependencies = Dependencies()

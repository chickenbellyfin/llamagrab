from typing import Mapping
from fastapi import Request
from fastapi.security.oauth2 import SecurityScopes
from fastapi_login.fastapi_login import LoginManager
from sqlalchemy.orm.session import Session, sessionmaker
from server_manager import ServerManager

from database.models import User

class Dependencies:
  def __init__(self):
    self._db_session = None
    self.login_manager = None

  def set(self, 
    db_session: sessionmaker ,
    login_manager: LoginManager,
    server_manager: ServerManager,
    regions: Mapping[str, str]):
    self._db_session = db_session
    self.login_manager = login_manager
    self._server_manager = server_manager
    self.regions = regions

  def db(self) -> Session:
    session: Session = self._db_session()
    try:
      yield session
    finally:
      session.close()

  def server_manager(self):
    return self._server_manager;

  async def login(self, request: Request, security_scopes: SecurityScopes = None) -> User:
    return await self.login_manager(request, security_scopes)

dependencies = Dependencies()
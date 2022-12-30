from loguru import logger
from passlib.hash import argon2

from api import flags, permissions
from api.audit import AuditLog
from api.auth import Auth
from api.database import queries
from api.database.database import Database
from api.database.models import User, UserLimits
from api.host_manager import HostManager
from api.service import exceptions
from api.service.server_service import ServerService


class AccountService:

  def __init__(self, 
    database: Database, 
    auth: Auth,
    servers: ServerService,
    host_manager: HostManager,
    audit: AuditLog
  ):
    self.database = database
    self.auth = auth
    self.servers = servers
    self.host_mananger = host_manager
    self.audit = audit
    
    # set of IPs which created an account
    self.account_create_ips = set()
  
  def _check_super(self, user: User):
    if not permissions.is_super(user):
      raise exceptions.PermissionsException()
  
  def create_auth_token(self, username, password):
    with self.database.session() as db:
      user = queries.get_user(db, username)

      if not user:
        # User does not exist
        raise exceptions.UnauthorizedException()
      
      self.auth.check_account_disabled_flags(user)

      if not argon2.verify(password, user.password):
        raise exceptions.UnauthorizedException()
      
      access_token = self.auth.login_manager.create_access_token(data=dict(sub=username))
      return access_token
      

  def create_account(self, username: str, password: str, source_ip: str):

    with self.database.session() as db:

      if flags.get_flag(db, 'disable_new_accounts'):
        logger.info(f"Blocked new account from IP {source_ip} because flag disable_new_accounts is enabled")
        raise exceptions.PermissionsException()
      
      # only allow 1 account to be created from a client address
      # this only persists during the lifetime of the process but probably good enough
      if source_ip in self.account_create_ips:
        logger.error(f'Client @ {source_ip} tried to create extra account: {username}')
        raise exceptions.LimitException()
      
      if queries.get_user(db, username) != None:
        raise exceptions.BadArgumentsException("User already exists")
      
      logger.info(f"Creating new user {username}")
      new_user = User(
        username=username,
        password=argon2.hash(password)
      )
      db.add(new_user)
      db.commit()
      db.add(UserLimits(user_id=new_user.id, server_limit=1, active_limit=1))
      db.commit()
      logger.info(f'Client @ {source_ip} created account: {new_user.username}')

    self.account_create_ips.add(source_ip)
    self.audit(new_user, 'account created')


  def set_password(self, new_password: str, current_password: str, user: User):
    if not argon2.verify(current_password, user.password):
      raise exceptions.UnauthorizedException('Current password is not correct')
    
    with self.database.session() as db:
      user.password = argon2.hash(new_password)
      db.merge(user)
      db.commit()

  def set_tribes_username(self, tribes_username: str, user: User):
    with self.database.session() as db:
      user.tribes_username = tribes_username
      db.merge(user)
      db.commit()
    self.audit(user, f'updated tribes username to {tribes_username}')

  def delete(self, user_id_to_delete: int, user: User):
    self._check_super(user)

    with self.database.session() as db:
      user_to_delete = queries.user_by_id(db, user_id_to_delete)
      if not user_to_delete:
        raise exceptions.NotFoundException()
      else:
        db.delete(user_to_delete)
        db.commit()
    self.host_mananger.sync()
    self.audit(user, f'deleted {user_to_delete}')
  
  def all(self):
    with self.database.session() as db:
      return db.query(User).all()



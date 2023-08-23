from loguru import logger
from passlib.hash import argon2

from api import permissions
from api.audit import AuditLog
from api.auth import Auth
from api.database import queries
from api.database.database import Database
from api.database.models import User, UserLimits
from api.flags import Flags
from api.host_manager import HostManager
from api.schema import validations
from api.service import exceptions
from api.service.server_service import ServerService


class AccountService:

  def __init__(self, 
    database: Database, 
    auth: Auth,
    servers: ServerService,
    host_manager: HostManager,
    flags: Flags,
    audit: AuditLog
  ):
    self.database = database
    self.auth = auth
    self.servers = servers
    self.host_mananger = host_manager
    self.flags = flags
    self.audit = audit
    
    # set of IPs which created an account
    self.account_create_ips = set()
  
  def _check_admin(self, user: User):
    if not permissions.is_admin(user):
      raise exceptions.PermissionsException()
    
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

      if self.flags.get_flag('disable_new_accounts'):
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
    try:
      validations.validate_password(new_password)
    except ValueError as e:
      raise exceptions.BadArgumentsException('New password is not valid')

    if current_password is None or not argon2.verify(current_password, user.password):
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
  
  def get(self, user_id) -> User:
    with self.database.session() as db:
      return queries.user_by_id(db, user_id)
  
  def verify_user(self, id_to_verify: int, user: User):
    self._check_admin(user)

    with self.database.session() as db:
      user_to_verify = queries.user_by_id(db, id_to_verify)
      if permissions.is_verified(user_to_verify):
        raise exceptions.BadArgumentsException()
      
      user_to_verify.tier = 'verified'
      user_to_verify.limits.server_limit = 5
      user_to_verify.limits.active_limit = 2
      db.commit()
    self.audit(user, f'updated {user_to_verify}\'s tier from unverified to verified')

  def make_admin(self, id_to_admin: int, user: User):
    self._check_super(user)

    with self.database.session() as db:
      user_to_admin = queries.user_by_id(db, id_to_admin)
      if permissions.is_admin(user_to_admin):
        raise exceptions.BadArgumentsException()
      old_tier = user_to_admin.tier
      user_to_admin.tier = 'admin'
      user_to_admin.limits.server_limit = None
      user_to_admin.limits.active_limit = None
      db.commit()
    self.audit(user, f'updated {user_to_admin}\'s tier from {old_tier} to admin')
  
  def make_not_admin(self, id_to_unadmin: int, user: User):
    self._check_super(user)

    with self.database.session() as db:
      user_to_unadmin = queries.user_by_id(db, id_to_unadmin)
      if not permissions.is_admin(user_to_unadmin) or permissions.is_super(user_to_unadmin):
        raise exceptions.BadArgumentsException()
      
      old_tier = user_to_unadmin.tier
      user_to_unadmin.tier = 'verified'
      user_to_unadmin.limits.server_limit = 5
      user_to_unadmin.limits.active_limit = 2
      db.commit()
    self.audit(user, f'updated {user_to_unadmin}\'s tier from {old_tier} to verified')

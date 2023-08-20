import time
from typing import Dict, List

from loguru import logger
from sqlalchemy.orm import Session

from api import permissions, server_history, server_sharing
from api.audit import AuditLog
from api.database import queries
from api.database.database import Database
from api.database.models import Server, User, ServerEditor
from api.host_manager import HostManager
from api.schema import responses
from api.schema.app_config import Region
from api.schema.game_server_config import GameServerConfig, GameType
from api.server_status import ServerStatusManager
from api.service import exceptions


class ServerService:

  def __init__(self, 
    database: Database, 
    host_manager: HostManager, 
    status_manager: ServerStatusManager,
    regions: Dict[str, Region],
    audit: AuditLog
  ):
    self.database = database
    self.host_manager = host_manager
    self.status_manager = status_manager
    self.regions = regions
    self.audit = audit

  def _get_server(self, server_id: int, user: User, db: Session) -> Server:
    server = queries.get_server(db, server_id)
    if server is None:
      raise exceptions.NotFoundException()
    elif not permissions.can_read_server(db, user, server):
      raise exceptions.PermissionsException()
    else:
      return server

  def get_server(self, server_id, user):
    with self.database.session() as db:
      return self._get_server(server_id, user, db)

  def get_server_status(self, server_id):
    with self.database.session() as db:
      server = queries.get_server(db, server_id)
      return responses.ServerStatus(
        id=server.id,
        owner=queries.user_by_id(db, server.user).username,
        name=server.name,
        region=server.region,
        region_name=self.regions[server.region].name if server.region in self.regions else server.region,
        enabled=server.enabled,
        status=self.status_manager.get_server_status(server),
        game=server.game,
        is_private=GameServerConfig.parse(server.server_config).password is not None
      )

  def create_server(
    self, 
    region: str,
    editors: List[int],
    game: GameType,
    config: GameServerConfig,
    user: User
  ):
    with self.database.session() as db:
      if not permissions.can_create_server(db, user):
        raise exceptions.LimitException("Server limit reached for user")

      now = int(time.time())
      new_server = Server(
        user=user.id,
        region=region,
        name=config.display_name,
        game=game,
        server_config=config.serialize(),
        updated_at=now,
        updated_by=user.id
      )
      db.add(new_server)
      db.commit()
    
      server_sharing.set_server_editors(db, new_server, editors or [])
      version = server_history.add_version(db, new_server)

    self.audit(user, f'created {new_server} with {version}')
    return new_server
  
  def update_settings(self,
    server_id: int,
    region: str,
    editors: List[int],
    user: User
  ):
    with self.database.session() as db:
      server = self._get_server(server_id, user, db)
      if not permissions.can_write_server(db, user, server):
        raise exceptions.PermissionsException
      
      new_editors = set(editors or [])
      old_editors = set([u.id for u in server_sharing.get_server_editors(db, server)])
      old_region = server.region
      # if editors was modified, check that the user has permission to share the server
      editors_changed = old_editors != new_editors
      if editors_changed and not permissions.can_share_server(user, server):
        raise exceptions.PermissionsException(f'User cannot modify editors of server')

      if region not in self.regions:
        raise exceptions.BadArgumentsException(f'Region {region} does not exist')
      
      server_sharing.set_server_editors(db, server, new_editors)
      server.region = region
      db.commit()
      self.host_manager.sync()

      if old_region != region:
        self.audit(user, f'updated region of {server} to {region}')
    
      if editors_changed:
        added = list(new_editors - old_editors)
        removed = list(old_editors - new_editors)
        self.audit(user, f'updated editors of {server} added={added} removed={removed}')
  
  def get_config(self, server_id: int, user: User):
    with self.database.session() as db:
      server = self._get_server(server_id, user, db)
      return GameServerConfig.parse(server.server_config)
  
  def set_config(self, server_id: int, config: GameServerConfig, user) -> int:
    with self.database.session() as db:
      server = self._get_server(server_id, user, db)

      if not permissions.can_write_server(db, user, server):
        raise exceptions.PermissionsException()

      server.name = config.display_name
      server.server_config = config.serialize()
      server.updated_at = int(time.time())
      server.updated_by = user.id
      version = server_history.add_version(db, server)
      db.commit()
    
    self.host_manager.sync()
    if version is not None:
      self.audit(user, f'updated configuration of {server} to {version}')
      
    return version.id


  def start_server(self, server_id, user: User):
    with self.database.session() as db:
      server = self._get_server(server_id, user, db)
      server.enabled = True
      db.commit()
    
    self.host_manager.sync()
    self.audit(user, f'started {server}')
  
  def stop_server(self, server_id, user: User):
    with self.database.session() as db:
      server = self._get_server(server_id, user, db)
      server.enabled = False
      db.commit()
    
    self.host_manager.sync()
    self.audit(user, f'stopped {server}')
  
  def restart_server(self, server_id, user: User):
    with self.database.session() as db:
      server = self._get_server(server_id, user, db)

    if self.status_manager.get_server_status(server) != 'running':
      raise exceptions.BadArgumentsException('Server is not running')
    
    self.host_manager.restart([server])
    self.audit(user, f'restarted {server}')
  
  def delete_server(self, server_id: int, user: User):
    with self.database.session() as db:      
      server = self._get_server(server_id, user, db)
      if server.user != user.id and user.tier != 'super':
        raise exceptions.PermissionsException()

      versions = server_history.get_versions(db, server)
      for version in versions:
        db.delete(version)
      db.query(ServerEditor).filter(ServerEditor.server_id == server.id).delete()
      db.delete(server)
      db.commit()

    self.host_manager.sync()
    self.audit(user, f'deleted {server}')
  
  def get_server_editors(self, server_id: int, user: User) -> List[User]:
    with self.database.session() as db:
      return server_sharing.get_server_editors(db, self._get_server(server_id, user, db))
  
  def get_versions(self, server_id: int, user: User):
    with self.database.session() as db:      
      server = self._get_server(server_id, user, db)
      return server_history.get_versions(db, server)
  
  def get_diff(self, server_id: int, version_id: int, user: User):
    with self.database.session() as db:      
      server = self._get_server(server_id, user, db)
      return server_history.get_diff(db, server, version_id)
  
  def get_owned_servers(self, user: User):
    with self.database.session() as db:
      return queries.get_servers(db, user)
  
  def get_shared_servers(self, user: User):
    with self.database.session() as db:
      return server_sharing.get_shared_servers(db, user)

import threading
from threading import Event
from typing import Mapping
from multiprocessing.connection import Client
from sqlalchemy.orm import Session
from sqlalchemy.orm.session import sessionmaker
from lua import LuaSettings
from schema.game_server_config import GameServerConfig
import database
import lua
import hashlib
import time
from database import queries

from loguru import logger

def md5(data: str) -> str:
  return hashlib.md5(data.encode('utf-8')).hexdigest()

def get_lua_settings(db: Session) -> LuaSettings:
  admin_users = queries.get_admin_tribes_usernames(db)
  return LuaSettings(include_admin=True, site_admins=admin_users)

class HostManager:
  """
  Handles syncing of server configs to ServerManager Agent instances on region hosts.
  When sync() is called (by the API or some other process), will return immediately and all of the
  running server's Lua's will be regenerated and sent to the nodes where they are supposed to be
  running.
  """

  def __init__(self,
    nodes: Mapping[str, str],
    port: int,
    auth_key: str,
    db_session: sessionmaker,
    rate_limit_secs=30):
    self.nodes = nodes
    self.port = port
    self.auth_key = auth_key.encode()
    self.session = db_session
    self.rate_limit_secs = rate_limit_secs
    self.event = Event()
    self.sync_requested = False
    self.last_sync_time = 0
    threading.Thread(target=self._worker, daemon=True).start()

  def _do_sync(self):
    with self.session() as db:
      logger.info(f'Running sync')
      lua_settings = get_lua_settings(db)
      for region in self.nodes:
        active_for_region = database.queries.get_active_servers(db, region)
        # Note: even if a region has no active servers, we should still sync so that newly stopped
        # servers are killed on the host
        payload = {}
        for server in active_for_region:
          server_config = GameServerConfig.parse(server.server_config)
          server_lua = lua.to_lua(server_config, lua_settings)
          payload[server.id] = server_lua

        message = {
          'type': 'sync',
          'payload': payload
        }
        
        message_hashed = { k: md5(payload[k]) for k in payload }
        logger.info(f'Syncing configs to {region}@{self.nodes[region]}:{self.port} {message_hashed}')

        try:
          with Client((self.nodes[region], self.port), authkey=self.auth_key) as connection:
            connection.send(message)
            connection.recv()
        except Exception as e:
          logger.error(f'Error while syncing to {region} - {type(e)}: {e}')

  def _wait_for_sync(self) -> bool:
    secs_since_last_sync = time.time() - self.last_sync_time
    if secs_since_last_sync < self.rate_limit_secs:
      time.sleep(self.rate_limit_secs - secs_since_last_sync)
    # todo maybe rewrite as a generator
    self.event.wait()
    should_sync = self.sync_requested
    self.sync_requested = False
    self.last_sync_time = time.time()
    self.event.clear()
    return should_sync


  def _worker(self):
    while True:
      try:
        should_sync = self._wait_for_sync()

        if should_sync:
          self._do_sync()
      except Exception as e:
        logger.opt(exception=True).error('Error while syncing')
  
  def sync(self):
    self.sync_requested = True
    self.event.set()


import hashlib
import threading
import time
from collections import namedtuple
from threading import Event

import requests
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy.orm.session import sessionmaker

from . import database, lua
from .database import queries
from .lua import LuaSettings
from .schema.game_server_config import GameServerConfig

Node = namedtuple('Node', 'name, host, token')

def md5(data: str) -> str:
  return hashlib.md5(data.encode('utf-8')).hexdigest()

def get_lua_settings(db: Session) -> LuaSettings:
  admin_users = queries.get_admin_tribes_usernames(db)
  return LuaSettings(include_admin=True, site_admins=admin_users)

class HostManager:
  """
  Handles syncing of server configs to Agent instances on region hosts.
  When sync() is called (by the API or some other process), will return immediately and all of the
  running server's Lua's will be regenerated and sent to the nodes where they are supposed to be
  running.
  """

  def __init__(self,
    nodes: dict,
    port: int,
    db_session: sessionmaker,
    rate_limit_secs=30):
    self.port = port
    self.session = db_session
    self.rate_limit_secs = rate_limit_secs
    self.event = Event()
    self.sync_requested = False
    self.last_sync_time = 0

    self.nodes = [
      Node(k, nodes[k]['host'], nodes[k]['token'])
      for k in nodes
    ]

    threading.Thread(target=self._worker, daemon=True).start()

  def _post(self, node: Node, command: str, payload=None):
    json = { 'type': command }
    if payload is not None:
      json['payload'] = payload
    try:
      response = requests.post(
        f'{node.host}:{self.port}/message',
        json=json,
        headers={'Token': node.token}
      )
      if not response.ok:
        return None
      return response.json()
    except Exception as e:
      logger.error(f'Error while sending {command} command to {node.name}- {type(e)}: {e}')
      return None


  def _do_sync(self):
    with self.session() as db:
      logger.info(f'Running sync')
      lua_settings = get_lua_settings(db)
      for node in self.nodes:
        active_for_region = database.queries.get_active_servers(db, node.name)
        # Note: even if a region has no active servers, we should still sync so that newly stopped
        # servers are killed on the host
        payload = {}
        for server in active_for_region:
          server_config = GameServerConfig.parse(server.server_config)
          server_lua = lua.to_lua(server, server_config, lua_settings)
          payload[server.id] = server_lua

        message_hashed = { k: md5(payload[k]) for k in payload }
        logger.info(f'Syncing configs to {node.name}@{node.host}:{self.port} {message_hashed}')
        self._post(node, 'sync', payload)



  def _wait_for_sync(self) -> bool:
    secs_since_last_sync = time.time() - self.last_sync_time
    if secs_since_last_sync < self.rate_limit_secs:
      time.sleep(max(0, self.rate_limit_secs - secs_since_last_sync))
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

  def status(self):
    return {
      node.name: self._post(node, 'status')
      for node in self.nodes
    }

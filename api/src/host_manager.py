import hashlib
import json
import threading
import time
from collections import namedtuple
from threading import Event

import requests
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy.orm.session import sessionmaker

from . import database, flags, lua
from .database import models, queries
from .lua import LuaSettings
from .schema.game_server_config import GameServerConfig

Node = namedtuple('Node', 'name, host, token')

def md5(data) -> str:
  val = json.dumps(data, sort_keys=True)
  return hashlib.md5(val.encode('utf-8')).hexdigest()[:7]

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

    self.nodes = {
      k: Node(k, nodes[k]['host'], nodes[k]['token'])
      for k in nodes
    }

    self.last_status = {
      k: None
      for k in nodes
    }

    threading.Thread(target=self._worker, daemon=True).start()

  def _request(self, method, node:Node, path: str, payload: object = None):
    kwargs = {}
    if payload is not None:
      kwargs = {'json': payload}
    try:
      response = method(
        f'{node.host}:{self.port}{path}',
        headers={'Token': node.token},
        **kwargs
      )
      if not response.ok:
        return None
      return response.json()
    except Exception as e:
      logger.error(f'Error requesting {node.name}:{path} - {type(e)}: {e}')
      return None

  def _do_sync(self):
    with self.session() as db:
      lua_settings = get_lua_settings(db)
      for node_name, node in self.nodes.items():
        active_for_region = database.queries.get_active_servers(db, node.name)
        # Note: even if a region has no active servers, we should still sync so that newly stopped
        # servers are killed on the host
        payload = {}
        for server in active_for_region:
          server_config = GameServerConfig.parse(server.server_config)
          server_lua = lua.to_lua(server, server_config, lua_settings)
          payload[server.id] = {
            'lua': server_lua,
            'loginserver': flags.get_flag(db, 'loginserver')
          }

        message_hashed = { k: md5(payload[k]) for k in payload }
        logger.info(f'Syncing configs to {node.name}@{node.host}:{self.port} {message_hashed}')
        self._update_status(
          node_name,
          self._request(requests.post, node, '/api/sync', payload)
        )

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

  def restart(self, server: models.Server):
    node = self.nodes.get(server.region)
    if node is None:
      logger.error(f'Region {server.region} does not exist')
      return

    self._update_status(server.region, self._request(requests.post, node, f'/api/restart/{server.id}'))


  def _update_status(self, region, status_response):
    if status_response is not None:
      self.last_status[region] = {
        int(k): v for k, v in status_response.items()
      }
    else:
      self.last_status[region] = None

  def status(self):
    for node_name, node in self.nodes.items():
      self._update_status(node_name, self._request(requests.get, node, '/api/status'))
    return self.last_status

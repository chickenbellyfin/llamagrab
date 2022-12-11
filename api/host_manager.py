import threading
import time
from threading import Event
from typing import Dict, List

import requests
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy.orm.session import sessionmaker

from api import flags, lua
from api.database import models, queries
from api.lua import LuaSettings
from api.schema.app_config import Region
from api.schema.game_server_config import GameServerConfig
from common import polling, concurrency, hashing


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
    regions: List[Region],
    port: int,
    db_session: sessionmaker,
    rate_limit_secs=10,
    periodic_sync=3600 * 2 
  ):
    self.port = port
    self.session = db_session

    self.regions: Dict[str, Region] = {
      r.key: r
      for r in regions
    }

    self.last_status = {
      r.key: None
      for r in regions
    }

    self.trigger_sync = polling.variable_rate(self._do_sync, periodic_sync, rate_limit_secs)


  def _request(self, method, region: Region, path: str, payload: object = None):
    kwargs = {}
    if payload is not None:
      kwargs = {'json': payload}
    try:
      response = method(
        f'{region.host}:{self.port}{path}',
        headers={'Token': region.token},
        **kwargs
      )
      if not response.ok:
        return None
      return response.json()
    except Exception as e:
      logger.error(f'Error requesting {region.name}:{path} - {type(e)}: {e}')
      return None

  @concurrency.synchronized
  def _do_sync(self):
    with self.session() as db:
      lua_settings = get_lua_settings(db)
      for region in self.regions.values():
        active_for_region = queries.get_active_servers(db, region.key)
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

        message_hashed = { k: hashing.md5(payload[k]) for k in payload }
        logger.info(f'Syncing configs to {region.name}@{region.host}:{self.port} {message_hashed}')
        self._update_status(
          region,
          self._request(requests.post, region, '/api/sync', payload)
        )

  def sync(self):
    self.trigger_sync()

  def restart(self, server: models.Server):
    region = self.regions.get(server.region)
    if region is None:
      logger.error(f'Region {server.region} does not exist')
      return

    self._update_status(region, self._request(requests.post, region, f'/api/restart/{server.id}'))


  def _update_status(self, region: Region, status_response):
    if status_response is not None:
      self.last_status[region.key] = {
        # convert server ids in response from str to int
        int(k): v for k, v in status_response.items()
      }
    else:
      self.last_status[region.key] = None

  def status(self):
    for region in self.regions.values():
      self._update_status(region, self._request(requests.get, region, '/api/status'))
    return self.last_status

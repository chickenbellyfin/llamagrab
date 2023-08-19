from collections import defaultdict
from typing import Dict, List

import requests
from loguru import logger
from sqlalchemy.orm import Session

from api import lua
from api.database import models, queries
from api.database.database import Database
from api.flags import Flags
from api.lua import LuaSettings
from api.schema.app_config import Region
from api.schema.game_server_config import GameServerConfig
from common import concurrency, hashing, polling


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
    regions: Dict[str, Region],
    port: int,
    database: Database,
    flags: Flags,
    rate_limit_secs=10,
    periodic_sync=3600 * 2 
  ):
    self.port = port
    self.database = database
    self.flags = flags
    self.regions = regions

    self.last_status = {
      r: None for r in regions
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
    with self.database.session() as db:
      lua_settings = get_lua_settings(db)
      active_per_region = {
        key: queries.get_active_servers(db, region=key) for key in self.regions
      }
    loginserver = self.flags.get_flag('loginserver')

    for region in self.regions.values():
      # Note: even if a region has no active servers, we should still sync so that newly stopped
      # servers are killed on the host
      payload = {}
      for server in active_per_region[region.key]:
        server_config = GameServerConfig.parse(server.server_config)
        server_lua = lua.to_lua(server, server_config, lua_settings)
        payload[server.id] = {
          'lua': server_lua,
          'loginserver': loginserver
        }

      message_hashed = { k: hashing.md5(payload[k]) for k in payload }
      logger.info(f'Syncing configs to {region.name}@{region.host}:{self.port} {message_hashed}')
      self._update_status(
        region,
        self._request(requests.post, region, '/api/sync', payload)
      )

  def sync(self):
    self.trigger_sync()

  def restart(self, servers: List[models.Server]):    
    by_region = defaultdict(list)
    for server in servers:
      by_region[server.region].append(server.id)

    for region_id, server_ids in by_region.items():
      region = self.regions.get(region_id)
      if region is None:
        logger.error(f'Region {region_id} does not exist')
      else:
        response = self._request(requests.post, region, f'/api/restart', server_ids)
        self._update_status(region, response)

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
  
  def banlist(self, ips: List[str]):
    logger.info(f'Pushing banlist with {len(ips)} items: {ips}')
    for region in self.regions.values():
      self._request(requests.post, region, '/api/banlist', ips)

  def iplogs(self):
    log = []
    for region in self.regions.values():
      response = self._request(requests.get, region, '/api/iplog')
      if response is not None:
        log.extend(response)
    
    return log

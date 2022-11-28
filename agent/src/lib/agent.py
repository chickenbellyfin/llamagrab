"""
ServerManager Agent - Service runs on each region's host server and listens for commands from
ServerManager API and runs taserver docker containers on the host accordingly.
"""
import json
import logging
import os
from logging import Logger
from typing import List

from .docker import Docker
from .hashing import md5


class Agent:

  def __init__(
    self,
    data_dir: str,
    docker: Docker,
    host_abs_data_dir: str = None,
    logger: Logger = logging.getLogger()
  ):
    self.gamesettings_dir = os.path.join(data_dir, 'managed_gamesettings')
    self.banlist = os.path.join(data_dir, 'banlist.txt')
    self.active_servers_file = os.path.join(data_dir, 'active_servers.json')

    # create empty banlist.txt
    if not os.path.exists(self.banlist):
      with open(self.banlist, 'w'):
        pass

    # If agent is running inside a container, the gamesettings mount path for taserver must be
    # relative to the host machine
    if host_abs_data_dir:
      self.host_gamesettings_dir = os.path.join(host_abs_data_dir, 'managed_gamesettings')
      self.host_banlist = os.path.join(host_abs_data_dir, 'banlist.txt')
    else:
      self.host_gamesettings_dir = self.gamesettings_dir
      self.host_banlist = self.banlist

    self.docker = docker
    self.logger = logger


  def host_path_for(self, server_id: int) -> str:
    return os.path.join(self.host_gamesettings_dir, f'server_{server_id}')

  def path_for(self, server_id: int) -> str:
    return os.path.join(self.gamesettings_dir, f'server_{server_id}')


  def get_current_active_servers(self):
    if os.path.exists(self.active_servers_file):
      with open(self.active_servers_file) as config_file:
        data = json.load(config_file)
        return {
          # convert server id keys to ints
          int(k): data[k] for k in data
        }
    else:
      return {}


  def write_active_servers(self, active_servers):
    for server_id in active_servers:
      server_dir = self.path_for(server_id)
      os.makedirs(server_dir, exist_ok=True)
      with open(os.path.join(server_dir, 'serverconfig.lua'), 'w') as lua_file:
        lua_file.write(active_servers[server_id]['lua'])

    with open(self.active_servers_file, 'w') as config_file:
      json.dump(active_servers, config_file, indent=2)

  def sync(self, active_servers):
    active_servers = {
      int(k): active_servers[k] for k in active_servers
    }
    active_hashes = {
      k: md5(active_servers[k]) for k in active_servers
    }
    self.logger.info(f'Received sync message: {active_hashes}')

    # load the previous config and write the new one
    old_active_servers = self.get_current_active_servers()
    self.write_active_servers(active_servers)

    # Detect changes
    changed = set()
    for server_id in active_servers:
      new_hash = md5(active_servers[server_id])
      if server_id not in old_active_servers:
        self.logger.info(f'server({server_id}) is being added to active servers hash={new_hash}')
        changed.add(server_id)
      elif active_servers[server_id] != old_active_servers[server_id]:
        old_hash = md5(old_active_servers[server_id])
        self.logger.info(f'server({server_id}) is being updated new={new_hash} old={old_hash}')
        changed.add(server_id)
      else:
        self.logger.info(f'server({server_id}) is unchanged')

    stopped = set(old_active_servers) - set(active_servers)
    for server_id in stopped:
      self.logger.info(f'server({server_id}) is being stopped')

    # Apply changes
    # Stop any deleted servers first to free up resources
    for server_id in stopped:
      self.logger.info(f'Stopping server({server_id})')
      self.docker.stop_server(server_id)

    running_servers = self.docker.status()
    used_port_offsets = set(running_servers.values())
    new_port_offset = 0

    for server_id in changed:
      server_path = self.host_path_for(server_id)

      # If the server exists, use the same port offest
      # for new servers, find an open port offset
      if server_id in running_servers:
        server_offset = running_servers[server_id]
        self.logger.info(f'Restarting server({server_id}) with offset {running_servers[server_id]}')
      else:
        while new_port_offset in used_port_offsets:
          new_port_offset += 2
        server_offset = new_port_offset
        used_port_offsets.add(new_port_offset)
        self.logger.info(f'Starting server({server_id}) with offset {new_port_offset}')

      self.docker.start_server(
        server_id=server_id, 
        offset=server_offset, 
        abs_gamesettings=server_path, 
        abs_banlist=self.host_banlist, 
        loginserver=active_servers[server_id].get('loginserver')
      )

  def restart(self, server_id):
    offsets = self.docker.status()
    active_servers = self.get_current_active_servers()
    if server_id not in offsets:
      logging.warn(f'Requested to restart {server_id} but it is not active on this host')
      return
    logging.info(f'Restarting {server_id}')
    self.docker.stop_server(server_id)
    self.docker.start_server(
      server_id=server_id, 
      offset=offsets[server_id], 
      abs_gamesettings=self.host_path_for(server_id), 
      abs_banlist=self.host_banlist,
      loginserver=active_servers[server_id].get('loginserver')
    )
    logging.info(f'Restarted {server_id}')


  def status(self):
    """ Return a list of server ids which are running"""
    return list(self.docker.status())

  def update_banlist(self, ips: List[str]):
    txt = ''
    for ip in ips:
      txt += f'{ip}\n'
    with open(self.banlist, 'w') as f:
      f.write(txt)
    return 'ok'

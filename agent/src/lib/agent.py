"""
ServerManager Agent - Service runs on each region's host server and listens for commands from
ServerManager API and runs taserver docker containers on the host accordingly.
"""
import json
import multiprocessing
import os
import time
from collections import namedtuple
from typing import List, Mapping, Set

from loguru import logger

from .docker import Docker
from .hashing import md5
from .util import start_polling, synchronized

AgentTask = namedtuple('AgentTask', 'action,expiry_time')

class Agent:

  def __init__(
    self,
    data_dir: str,
    docker: Docker,
    host_abs_data_dir: str = None,
    max_concurrency=None,
    interval_secs=15,
    container_start_time_secs=40
  ):
    self.gamesettings_dir = os.path.join(data_dir, 'managed_gamesettings')
    self.banlist = os.path.join(data_dir, 'banlist.txt')
    self.active_servers_file = os.path.join(data_dir, 'active_servers.json')
    
    if max_concurrency is None:
      self.max_concurrency = multiprocessing.cpu_count() # TODO: try 2n-1, ceil(1.5n), etc
      logger.info(f"Container start concurrency is {self.max_concurrency} based on CPUs ({multiprocessing.cpu_count()})")
    else:
      self.max_concurrency = max_concurrency
      logger.info(f"Container start concurrency is set to {max_concurrency}")
    self.interval_secs = interval_secs
    self.container_start_time_secs = container_start_time_secs

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

    # used only by _log_tasks()
    self._log_tasks_was_nonzero = False

    # track ongoing server starts/restarts
    self.tasks: Mapping[int, AgentTask] = {}
    self.requested_restarts: Set[int] = set()
  
  def start(self):    
    start_polling(self._check_servers, self.interval_secs)


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

  def _log_tasks(self):
    # we log when there are ongoing tasks, and log once more after all the tasks have completed
    if len(self.tasks) > 0 or self._log_tasks_was_nonzero:
      now = time.time()
      task_str = []
      for server_id, task in self.tasks.items():
        task_str.append(f"(server {server_id}, {task.expiry_time - now:.0f}s)")
      logger.info(f"{len(self.tasks)} Ongoing Tasks: {' '.join(task_str)}   Restart Queue: [{' '.join(map(str, self.requested_restarts))}]")
    self._log_tasks_was_nonzero = len(self.tasks) > 0

  @synchronized
  def _check_servers(self):
    current_time = time.time()
    
    # remove tasks which have timed out
    self.tasks = {
      k: v
      for k, v in self.tasks.items()
      if v.expiry_time > current_time
    }
    
    if  self.max_concurrency - len(self.tasks) == 0:
      # skip if we are already running the max number of tasks
      self._log_tasks()
      return
    
    active_servers = self.get_current_active_servers()
    running_servers = self.docker.status()

    pending_tasks = {}

    for server_id in active_servers:
      if server_id not in running_servers:
        pending_tasks[server_id] = 'start'
      elif md5(active_servers[server_id]) != running_servers[server_id].hash:
        pending_tasks[server_id] = 'restart'
    
    for server_id in self.requested_restarts:
      if server_id not in active_servers:
        logger.info(f"requested restart server({server_id}) but it is not active")
        self.requested_restarts.discard(server_id)
      elif server_id not in pending_tasks:
        pending_tasks[server_id] = 'restart'
    
    if len(pending_tasks) == 0:
      self._log_tasks()
      return

    logger.info(f"{len(pending_tasks)} pending server start tasks")


    used_port_offsets = set([c.port_offset for c in running_servers.values()])
    new_port_offset = 0

    for server_id, action in pending_tasks.items():
      if server_id not in self.tasks:      
        # If the server exists, use the same port offest
        # for new servers, find an open port offset
        if server_id in running_servers:
          server_offset = running_servers[server_id].port_offset
          logger.info(f'Restarting server({server_id}) with offset {server_offset}')
        else:
          while new_port_offset in used_port_offsets:
            new_port_offset += 2
          server_offset = new_port_offset
          used_port_offsets.add(new_port_offset)
          logger.info(f'Starting server({server_id}) with offset {server_offset}')

        # start and restart are the same operation
        self.docker.start_server(
          server_id=server_id, 
          offset=server_offset, 
          abs_gamesettings=self.host_path_for(server_id), 
          abs_banlist=self.host_banlist, 
          hash=md5(active_servers[server_id]),
          loginserver=active_servers[server_id].get('loginserver')
        )

        self.tasks[server_id] = AgentTask(action, time.time() + self.container_start_time_secs)
        self.requested_restarts.discard(server_id)

        if len(self.tasks) == self.max_concurrency:
          break

    self._log_tasks()
    

  def sync(self, active_servers):
    active_servers = {
      int(k): active_servers[k] for k in active_servers
    }
    active_hashes = {
      k: md5(active_servers[k]) for k in active_servers
    }
    logger.info(f'Received sync message: {active_hashes}')

    # load the previous config and write the new one
    old_active_servers = self.get_current_active_servers()
    self.write_active_servers(active_servers)

    running_servers = self.docker.status()

    # Detect changes
    for server_id in active_servers:
      new_hash = md5(active_servers[server_id])
      if server_id not in old_active_servers:
        logger.info(f'server({server_id}) is being added hash={new_hash}')
      elif active_servers[server_id] != old_active_servers[server_id]:
        old_hash = md5(old_active_servers[server_id])
        logger.info(f'server({server_id}) is being updated new={new_hash} old={old_hash}')
      elif server_id not in running_servers:
        logger.info(f'server({server_id}) is supposed to be running but isn\'t. hash={new_hash}')
      else:
        logger.info(f'server({server_id}) is unchanged')

    stopped = set(old_active_servers) - set(active_servers)
    for server_id in stopped:
      logger.info(f'server({server_id}) is being stopped')

    # Apply changes
    # Stop any deleted servers first to free up resources
    for server_id in stopped:
      logger.info(f'Stopping server({server_id})')
      self.docker.stop_server(server_id)
    
    self._check_servers()
    return self.status()


  def restart(self, server_id):
    active = self.get_current_active_servers()
    if server_id not in active:
      logger.warn(f'Requested to restart {server_id} but it is not active on this host')
      return
    logger.info(f'Restarting {server_id}')
    self.requested_restarts.add(server_id)
    self._check_servers()
    return self.status()


  def status(self) -> Mapping[int, str]:
    """ Return a map of server id to status (running, starting, restarting)"""
    active = self.get_current_active_servers()
    running = self.docker.status()
    statuses = {}

    for server_id in active:
      is_restart_requested = server_id in self.requested_restarts
      is_restarting = server_id in self.tasks and self.tasks[server_id].action == 'restart'
      is_running = server_id in running
      is_starting = server_id in self.tasks and self.tasks[server_id].action == 'start'
      
      if is_restart_requested or is_restarting:
        statuses[server_id] = 'restarting'
      elif not is_running or is_starting:
        statuses[server_id] = 'starting'
      else:
        statuses[server_id] = 'running'
      
    return statuses

  def update_banlist(self, ips: List[str]):
    txt = ''
    for ip in ips:
      txt += f'{ip}\n'
    with open(self.banlist, 'w') as f:
      f.write(txt)
    return 'ok'

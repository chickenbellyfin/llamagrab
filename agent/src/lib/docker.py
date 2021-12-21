import json
import logging
import subprocess
from typing import Mapping

logger = logging.getLogger(__name__)


class Docker:

  def __init__(self, use_host_networking: bool = False, loginserver: str = None, image = 'taserver'):
    self.use_host_networking = use_host_networking
    self.loginserver = loginserver
    self.image = image
  
  def _container_name(self, server_id):
    return f'taserver_{server_id}'

  def status(self) -> Mapping[int, int]:
    try:
      ps_result = subprocess.check_output(['docker', 'ps', '-q']).decode()
      if len(ps_result):
        output = subprocess.check_output('docker inspect $(docker ps -q)', shell=True)
      else:
        return {}
    except subprocess.CalledProcessError as e:
      logger.error(e, exc_info=True)
      return {}
  
    docker_inspect = json.loads(output)
    running_containers = {}

    for container in docker_inspect:
      # Name is /taserver_$id
      if not container['Name'].startswith('/taserver_'):
        continue
      
      server_id = int(container['Name'].split('_')[1])
      
      bindings = container['HostConfig']['PortBindings']
      # binding is "PORT/proto": [{"HostIp": "", "HostPort": "PORT"}]
      offset = None
      for binding in bindings:
        port = int(binding.split('/')[0])
        if port > 9000: # if its the launcher port
          offset = port - 9002
          break
      if offset is not None:
        running_containers[server_id] = offset

    return running_containers

  def start_server(self, server_id: int, offset: int, abs_gamesettings: str) -> None:
    name = self._container_name(server_id)
    
    gameserver1_port = 7777 + offset
    gameserver2_port = 7778 + offset
    control_port = 9002 + offset

    self.stop_server(server_id)

    options = [
      '--name', name,
      '-v', f'{abs_gamesettings}:/gamesettings',
      '-d', '--restart', 'unless-stopped',
      '--cap-add', 'NET_ADMIN',
      '-p', f'{gameserver1_port}:{gameserver1_port}/tcp',
      '-p', f'{gameserver1_port}:{gameserver1_port}/udp',
      '-p', f'{gameserver2_port}:{gameserver2_port}/tcp',
      '-p', f'{gameserver2_port}:{gameserver2_port}/udp',
      '-p', f'{control_port}:{control_port}/tcp',
      '-p', f'{control_port}:{control_port}/udp',
    ]

    # If the login server is on the same host as the container, use host networking so that 
    # the ip address is detected correctly
    if self.use_host_networking:
      options += ['--network', 'host']
    
    # set environment var for login server host
    if self.loginserver:
      options += ['-e', f'LOGINSERVER={self.loginserver}']

    args = ['docker', 'run'] + options + [self.image, f'--port-offset={offset}']
    command = ' '.join(args)
    logger.info(f'Running {command}')
    subprocess.call(args)

  def stop_server(self, server_id: int) -> None:
    name = self._container_name(server_id)
    args = ['docker', 'rm', '-f', name]
    command = ' '.join(args)
    logger.info(f'Running {command}')
    subprocess.call(args)


class NullDocker:
  
  def __init__(self):
    self.running = {}

  def status(self) -> Mapping[int, int]:
    return self.running.copy()

  def start_server(self, server_id: int, offset: int, abs_gamesettings: str) -> None:
    self.running[server_id] = offset

  def stop_server(self, server_id: int) -> None:
    if server_id in self.running:
      self.running.pop(server_id)

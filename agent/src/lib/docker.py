import logging
from typing import Mapping

logger = logging.getLogger(__name__)


class Docker:

  def __init__(self, docker_client, use_host_networking: bool = False, loginserver: str = None, image = 'taserver'):
    self.use_host_networking = use_host_networking
    self.loginserver = loginserver
    self.image = image
    self.client = docker_client
  
  def _container_name(self, server_id):
    return f'taserver_{server_id}'

  def status(self) -> Mapping[int, int]:
    containers = self.client.containers.list()
    taservers = filter(lambda c: 'llamagrab' in c.labels, containers)
    running_containers = {}

    for container in taservers:      
      server_id = int(container.labels['server_id'])
      port_offset = int(container.labels['port_offset'])
      running_containers[server_id] = port_offset

    return running_containers

  def start_server(self, server_id: int, offset: int, abs_gamesettings: str) -> None:
    name = self._container_name(server_id)
    
    gameserver1_port = 7777 + offset
    gameserver2_port = 7778 + offset
    control_port = 9002 + offset

    if self.use_host_networking:
      port_mappings = None
      network_mode = 'host'
    else:
      port_mappings = {
        f'{gameserver1_port}/tcp': gameserver1_port,
        f'{gameserver1_port}/udp': gameserver1_port,
        f'{gameserver2_port}/tcp': gameserver2_port,
        f'{gameserver2_port}/udp': gameserver2_port,
        f'{control_port}/tcp': control_port,
        f'{control_port}/udp': control_port,
      }
      network_mode = None

    self.stop_server(server_id)    
    logging.info(f'Running container {name} offset={offset} ports={gameserver1_port},{gameserver2_port},{control_port} path={abs_gamesettings}')
    self.client.containers.run(
      self.image,
      command = [f'--port-offset={offset}'],
      name = name,
      labels = {
        'llamagrab': '', # makes it easy to filter containers to get status
        'server_id': f'{server_id}',
        'port_offset': f'{offset}'
      },
      volumes = [f'{abs_gamesettings}:/gamesettings'],
      detach = True,
      restart_policy = {'Name': 'unless-stopped'},
      cap_add = ['NET_ADMIN'],
      ports = port_mappings,      
      environment = [f'LOGINSERVER={self.loginserver}'] if self.loginserver else None,
      # If the login server is on the same host as the container, use host networking so that 
      # the ip address is detected correctly
      network_mode = network_mode
    )

  def stop_server(self, server_id: int) -> None:
    name = self._container_name(server_id)

    try:
      server = self.client.containers.get(name)
      server.remove(force=True)
      logger.info(f'Removed {name}')
    except Exception as e:
      # Not found, ignore
      pass


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

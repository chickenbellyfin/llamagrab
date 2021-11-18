
import logging
import os
import sys
from typing import List
import yaml

from hashing import md5
from agent import Agent
from docker import Docker, NullDocker

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s :: %(levelname)s :: %(name)s :: %(message)s',
  handlers=[
    logging.FileHandler("agent.log"),
    logging.StreamHandler()
  ]
)
logger = logging.getLogger()

def main(argv: List[str]):
  logger.info('Starting...')

  config_path = 'config.yaml'
  if len(argv) > 1:
    config_path = argv[1]

  logger.info(f'Reading config from {config_path}')
  with open(config_path) as config_file:
    config = yaml.safe_load(config_file)

  gamesettings_dir = os.path.abspath(config['gamesettings_dir'])
  auth_key = config['auth_key'].encode()
  port = int(config['port'])
  testing = config.get('testing', False)

  docker = NullDocker() if testing else Docker()

  agent = Agent(
    gamesettings_dir=gamesettings_dir,
    auth_key=auth_key,
    address=('0.0.0.0', port),
    docker=docker
  )

  active_servers = agent.get_current_active_servers()
  active_hashes = {
    k: md5(active_servers[k]) for k in active_servers
  }
  logger.info(f'Current active servers: {active_hashes}')
  agent.start().join()



if __name__ == '__main__':
  main(sys.argv)
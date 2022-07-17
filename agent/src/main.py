
import logging
import os
import sys
from typing import Dict, List, Set

import docker as docker_lib
import uvicorn
import yaml
from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import HTTPException


from .lib.agent import Agent
from .lib.docker import Docker, NullDocker
from .lib.hashing import md5

logger = logging.getLogger()

MESSAGE_TYPES = {
  'sync', 'status', 'ping'
}

def create_app(agent: Agent, tokens: Set[str]):
  app = FastAPI()

  def auth(request: Request):
    request_token = request.headers.get('token')
    if request_token is None or request_token not in tokens:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    pass

  @app.post('/api/sync')
  def handle_sync(servers: Dict[int, str], auth=Depends(auth)):
    logging.info(servers)
    agent.sync(servers)
    return 'ok'

  @app.get('/api/status')
  def handle_status(auth=Depends(auth)):
    return agent.status()

  @app.post('/api/ping')
  def handle_ping(auth=Depends(auth)):
    return 'pong'

  return app


def main(argv: List[str]):
  logger.info('Starting...')

  data_dir = ''
  if len(argv) > 1:
    data_dir = argv[1]

  logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s :: %(levelname)s :: %(name)s :: %(message)s',
    handlers=[
      logging.FileHandler(os.path.join(data_dir, 'agent.log')),
      logging.StreamHandler()
    ]
  )

  config_path = os.path.join(data_dir, 'config.yaml')

  logger.info(f'Reading config from {config_path}')
  with open(config_path) as config_file:
    config = yaml.safe_load(config_file)

  host_abs_data_dir = config.get('host_abs_data_dir')
  port = int(config['port'])
  testing = config.get('testing', False)
  loginserver = config.get('loginserver', None)
  use_host_networking = config.get('use_host_networking', False)
  image = config.get('image', 'taserver')
  tokens = config.get('tokens', [])

  docker = NullDocker() if testing else Docker(
    docker_lib.from_env(),
    use_host_networking=use_host_networking,
    loginserver=loginserver,
    image=image
  )

  agent = Agent(
    data_dir=data_dir,
    docker=docker,
    host_abs_data_dir=host_abs_data_dir
  )

  active_servers = agent.get_current_active_servers()
  active_hashes = {
    k: md5(active_servers[k]) for k in active_servers
  }
  logger.info(f'Current active servers: {active_hashes}')

  app = create_app(agent, tokens=set(tokens))
  uvicorn.run(app, host='0.0.0.0', port=port)


if __name__ == '__main__':
  main(sys.argv)

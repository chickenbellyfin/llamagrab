
import logging
import os
import sys

import docker as docker_lib
from fastapi.exceptions import HTTPException
from fastapi import FastAPI, Request, status
from typing import List, Set
import yaml
import uvicorn

from .lib.hashing import md5
from .lib.agent import Agent
from .lib.docker import Docker, NullDocker

logger = logging.getLogger()


def create_app(agent: Agent, tokens: Set[str]):
  app = FastAPI()

  @app.post('/message')
  async def handle_message(request: Request):
    request_token = request.headers.get('token')
    if request_token is None or request_token not in tokens:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    try:
      json = await request.json()
      result = agent.handle_message(json)
    except:
      logger.exception(f'Exception while handling request')
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if not result:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

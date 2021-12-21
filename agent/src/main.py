
import logging
import os
import sys

from fastapi.exceptions import HTTPException
from fastapi import FastAPI, Request, status
from typing import List
import yaml
import uvicorn

from .lib.hashing import md5
from .lib.agent import Agent
from .lib.docker import Docker, NullDocker

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s :: %(levelname)s :: %(name)s :: %(message)s',
  handlers=[
    logging.FileHandler("agent.log"),
    logging.StreamHandler()
  ]
)
logger = logging.getLogger()


def create_app(agent: Agent):
  app = FastAPI()

  @app.post('/message')
  async def handle_message(request: Request):
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

  config_path = 'config.yaml'
  if len(argv) > 1:
    config_path = argv[1]

  logger.info(f'Reading config from {config_path}')
  with open(config_path) as config_file:
    config = yaml.safe_load(config_file)

  gamesettings_dir = os.path.abspath(config['gamesettings_dir'])
  port = int(config['port'])
  testing = config.get('testing', False)
  use_host_networking = config.get('use_host_networking', False)

  docker = NullDocker() if testing else Docker(use_host_networking=use_host_networking)

  agent = Agent(
    gamesettings_dir=gamesettings_dir,
    docker=docker
  )

  active_servers = agent.get_current_active_servers()
  active_hashes = {
    k: md5(active_servers[k]) for k in active_servers
  }
  logger.info(f'Current active servers: {active_hashes}')
  
  app = create_app(agent)
  uvicorn.run(app, host='0.0.0.0', port=port)


if __name__ == '__main__':
  main(sys.argv)

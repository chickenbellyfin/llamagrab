
import logging
import os
import sys
from typing import Dict, List, Set
from ipaddress import ip_interface

import docker as docker_lib
import uvicorn
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
    agent.sync(servers)
    return 'ok'

  @app.post('/api/restart/{server_id}')
  def handle_restart(server_id: int, auth=Depends(auth)):
    agent.restart(server_id)
    return ''

  @app.get('/api/status')
  def handle_status(auth=Depends(auth)):
    return agent.status()

  @app.post('/api/banlist')
  def handle_update_banlist(ips: List[str], auth=Depends(auth)):
    def validate_ip(ip: str):
      try:
        ip_interface(ip)
        return True
      except:
        return False

    if not all(map(validate_ip, ips)):
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return agent.update_banlist(ips)

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

  host_abs_data_dir = os.environ.get('LG_HOST_ABS_DATA_DIR')
  port = int(os.environ.get('LG_PORT', 8999))
  testing = os.environ.get('LG_TESTING', 'true').lower() == 'true'
  loginserver = os.environ.get('LG_LOGINSERVER')
  use_host_networking = os.environ.get('LG_USE_HOST_NETWORKING', 'false') == 'true'
  image = os.environ.get('LG_TASERVER_IMAGE', 'taserver')
  # tokens are comma separated non-empty strings
  tokens = [
    token.strip() for token in
    os.environ.get('LG_TOKENS', '').split(',')
    if len(token.strip()) > 0
  ]

  if len(tokens) == 0:
    logger.error(f'LG_TOKENS env not set. At least 1 auth token is required.')
    exit(1)

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

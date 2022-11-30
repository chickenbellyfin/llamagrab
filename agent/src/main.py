
import os
import sys
from ipaddress import ip_interface
from typing import Any, Dict, List, Set

import docker as docker_lib
import uvicorn
from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import HTTPException
import logging
from loguru import logger

from .lib.agent import Agent
from .lib.docker import Docker, NullDocker
from .lib.hashing import md5

MESSAGE_TYPES = {
  'sync', 'status', 'ping'
}

# https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = sys._getframe(6), 6
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

def create_app(agent: Agent, tokens: Set[str]):
  app = FastAPI()

  def auth(request: Request):
    request_token = request.headers.get('token')
    if request_token is None or request_token not in tokens:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    pass

  @app.post('/api/sync')
  def handle_sync(servers: Dict[int, Any], auth=Depends(auth)):
    return agent.sync(servers)

  @app.post('/api/restart/{server_id}')
  def handle_restart(server_id: int, auth=Depends(auth)):
    return agent.restart(server_id)

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
  logger.info('Starting Agent...')

  data_dir = ''
  if len(argv) > 1:
    data_dir = argv[1]

  # uvicorn http logs are filtered out to access.log
  logger.add(os.path.join(data_dir, 'app.log'), rotation='10 MB', filter={
    'uvicorn.protocols.http': False
  })
  logger.add(os.path.join(data_dir, 'access.log'), rotation='10 MB', filter='uvicorn.protocols.http')
  logger.disable('urllib3')

  host_abs_data_dir = os.environ.get('LG_HOST_ABS_DATA_DIR')
  port = int(os.environ.get('LG_PORT', 8999))
  testing = os.environ.get('LG_TESTING', 'true').lower() == 'true'
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
  agent.start()
  uvicorn.run(
    app, 
    host='0.0.0.0', 
    port=port,    
    log_config=None,
    proxy_headers=True,
    forwarded_allow_ips="*" # allows uvicorn to access log with IPs forwarded by reverse proxy (caddy)
  )


if __name__ == '__main__':
  main(sys.argv)

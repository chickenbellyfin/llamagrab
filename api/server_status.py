from loguru import logger

from api.database import models
from api.host_manager import HostManager
from common import polling


class ServerStatusManager:
  """
    Handles fetching & tracking server statuses from HostManager
    Compares running status with the servers's desired state to derive status as one of:
        offline, stopping, starting, running
  """
  def __init__(
    self, host_manager: HostManager,
    min_polling_rate: int = 60,
    max_polling_rate: int = 10,
    max_polling_timeout: int = 60
  ):
    self.host_manager = host_manager
    logger.info(f'ServerStatusManager polling rate min={min_polling_rate}s max={max_polling_rate}s, timeout={max_polling_timeout}')
    self.trigger_status = polling.variable_rate(self.host_manager.status, min_polling_rate, max_polling_rate, max_polling_timeout)


  def get_region_status(self, region_key: str):
    self.trigger_status()
    return self.host_manager.last_status.get(region_key) is not None


  def get_server_status(self, server: models.Server) -> str:
    self.trigger_status()
    enabled = server.enabled
    last_status = self.host_manager.last_status.get(server.region)
    region = server.region is not None and last_status is not None # is region up?
    
    if last_status is not None and server.id in last_status:
      # we have the actual status from the region so use that
      status = last_status[server.id]
    else:
      # the region is up, but server is not in latest region status
      status = 'starting'
    
    running = last_status is not None and server.id in last_status
    if not enabled:
      if not running:
        return 'disabled'
      else:
        return 'stopping'
    else:
      if not region:
        return 'unknown'
      else:
        return status

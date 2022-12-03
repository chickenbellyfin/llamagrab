import threading
import time

from loguru import logger

from api.database import models
from api.host_manager import HostManager


class ServerStatusManager:
  """
    Handles fetching & tracking server statuses from HostManager
    Compares running status with the servers's desired state to derive status as one of:
        offline, stopping, starting, running
  """
  def __init__(
    self, host_manager:
    HostManager,
    polling_rate: int = 10
  ):
    self.host_manager = host_manager
    self.polling_rate = polling_rate
    logger.info(f'ServerStatusManager poll_interval = {polling_rate}s')
    self._thread = threading.Thread(target=self._poller, daemon=True)
    self._polling = True
    self._thread.start()


  def _poller(self):
    while self._polling:
      self.host_manager.status()
      time.sleep(self.polling_rate)

  def get_region_status(self, region):
    return self.host_manager.last_status.get(region) is not None


  def get_server_status(self, server: models.Server) -> str:
    enabled = server.enabled
    last_status = self.host_manager.last_status.get(server.region)
    region = server.region is not None and last_status is not None # is region up?
    
    if last_status is not None and server.id in last_status:
      # we have the actual status from the region so use that
      status = last_status[server.id]
    else:
      # region is up, but server is not in latest region status
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

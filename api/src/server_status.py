from loguru import logger
import threading
import time

from .database import models
from .host_manager import HostManager

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
    self.host_statuses = {}
    logger.info(f'ServerStatusManager poll_interval = {polling_rate}s')
    self._thread = threading.Thread(target=self._poller, daemon=True)
    self._polling = True
    self._thread.start()


  def _poller(self):
    while self._polling:
        self.host_statuses = self.host_manager.status()
        time.sleep(self.polling_rate)


  def get_region_status(self, region):
    return self.host_statuses.get(region) is not None


  def get_server_status(self, server: models.Server) -> str:
    enabled = server.enabled
    region = server.region is not None and self.host_statuses.get(server.region) is not None
    running = self.host_statuses.get(server.region) is not None and  server.id in self.host_statuses.get(server.region, [])

    if not enabled:
      if not running:
        return 'disabled'
      else:
        return 'stopping'
    else:
      if not region:
        return 'unknown'
      else:
        if not running:
          return 'starting'
        else:
          return 'running'

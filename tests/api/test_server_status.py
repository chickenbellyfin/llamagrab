import time
from typing import Callable, Tuple
from unittest.mock import MagicMock

import pytest

from api.database.models import Server
from api.host_manager import HostManager
from api.server_status import ServerStatusManager

TEST_SERVER_ID = 23

def wait_for(assertion: Callable[[], bool], wait_time=1, interval=0.001) -> Tuple[float, int]:
  """ wait for assertion to be true, if timeout assert false"""
  start_time = time.time()
  tries = 0
  while time.time() - start_time < wait_time:
    tries += 1
    result = assertion()
    if result:
      return (time.time() - start_time, tries)
    time.sleep(interval)
  return (time.time() - start_time, tries)

def server_with(enabled=False, region='test_region'):
  return Server(
    id=TEST_SERVER_ID,
    user=54,
    name='Status Test Server',
    region=region,
    enabled=enabled,
    server_config='{}'
  )

@pytest.fixture
def host_manager() -> HostManager:
  return MagicMock()


def test_region_status_empty(host_manager: HostManager):
  host_manager.last_status = {}
  status_manager = ServerStatusManager(host_manager)
  wait_for(lambda: host_manager.status.called)
  assert status_manager.get_region_status('test_region') == False

def test_region_status_failed(host_manager: HostManager):
  host_manager.last_status = {'test_region': None}
  status_manager = ServerStatusManager(host_manager)
  wait_for(lambda: host_manager.status.called)
  assert status_manager.get_region_status('test_region') == False

def test_region_status_good(host_manager: HostManager):
  host_manager.last_status = {'test_region': []}
  status_manager = ServerStatusManager(host_manager)
  wait_for(lambda: host_manager.status.called)
  assert status_manager.get_region_status('test_region') == True

def test_server_disabled_not_running(host_manager: HostManager):
  host_manager.last_status = {'test_region': []}
  status_manager = ServerStatusManager(host_manager)
  wait_for(lambda: host_manager.status.called)
  assert status_manager.get_server_status(server_with(enabled=False)) == 'disabled'

def test_server_disabled_not_running_region_down(host_manager: HostManager):
  host_manager.last_status = {'test_region': None}
  status_manager = ServerStatusManager(host_manager)
  wait_for(lambda: host_manager.status.called)
  assert status_manager.get_server_status(server_with(enabled=False)) == 'disabled'

def test_server_disabled_running(host_manager: HostManager):
  host_manager.last_status = {'test_region': {34: 'running',TEST_SERVER_ID: 'running', 45: 'running'}}
  status_manager = ServerStatusManager(host_manager)
  wait_for(lambda: host_manager.status.called)
  assert status_manager.get_server_status(server_with(enabled=False)) == 'stopping'

def test_server_enabled_region_down(host_manager: HostManager):
  host_manager.last_status = {'test_region': None, 'other_region': {}}
  status_manager = ServerStatusManager(host_manager)
  wait_for(lambda: host_manager.status.called)
  assert status_manager.get_server_status(server_with(enabled=True)) == 'unknown'

def test_server_enabled_not_running(host_manager: HostManager):
  host_manager.last_status = {'test_region': {}, 'other_region': {}}
  status_manager = ServerStatusManager(host_manager)
  wait_for(lambda: host_manager.status.called)
  assert status_manager.get_server_status(server_with(enabled=True)) == 'starting'

def test_server_enabled_running(host_manager: HostManager):
  host_manager.last_status = {'test_region': {TEST_SERVER_ID: 'running'}, 'other_region': {}}
  status_manager = ServerStatusManager(host_manager)
  wait_for(lambda: host_manager.status.called)
  assert status_manager.get_server_status(server_with(enabled=True)) == 'running'

def test_server_enabled_whatever(host_manager: HostManager):
  # pass through whatever region says
  host_manager.last_status = {'test_region': {TEST_SERVER_ID: 'whatever'}, 'other_region': {}}
  status_manager = ServerStatusManager(host_manager)
  wait_for(lambda: host_manager.status.called)
  assert status_manager.get_server_status(server_with(enabled=True)) == 'whatever'

def test_server_enabled_running_wrong_region(host_manager: HostManager):
  host_manager.last_status = {'other_region': {TEST_SERVER_ID: 'running'}, 'test_region': {}}
  status_manager = ServerStatusManager(host_manager)
  wait_for(lambda: host_manager.status.called)
  assert status_manager.get_server_status(server_with(enabled=True)) == 'starting'

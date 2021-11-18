from unittest import mock
import pytest
# import unittest
from unittest.mock import Mock, patch, call
from subprocess import CalledProcessError
from docker import Docker, NullDocker

# Sample inspect output from a live server w/ 3 taservers
# $ docker inspect $(docker ps -q) > out.json
with open('tests/sample_inspect.json') as f:
  sample_inspect = f.read().encode()
sample_inspect_ps_q = "fc7561ad6fc2\n7e567f6b7777\n63c3da5c16b3".encode()

# class DocketTest(unittest.TestCase):
@pytest.fixture
def mock_subprocess():
  with patch('docker.subprocess') as mock:
    yield mock

def test_status_empty(mock_subprocess):
  mock_subprocess.check_output.return_value = b''
  docker = Docker()
  result = docker.status()
  assert {} == result
  mock_subprocess.check_output.assert_called_once_with([
    'docker', 'ps', '-q'
  ])

def test_status_error(mock_subprocess):
  def problem(args):
    raise CalledProcessError(1, args)
  mock_subprocess.check_output.side_effect = problem
  mock_subprocess.CalledProcessError = CalledProcessError
  docker = Docker()
  result = docker.status()
  assert {} == result
  mock_subprocess.check_output.assert_called_once_with([
    'docker', 'ps', '-q'
  ])


def test_status(mock_subprocess):
  mock_subprocess.check_output.side_effect = [
    sample_inspect_ps_q,
    sample_inspect
  ]
  docker = Docker()
  result = docker.status()
  assert {
    111: 6,
    222: 2,
    333: 0
  } == result
  mock_subprocess.check_output.assert_has_calls([
    call(['docker', 'ps', '-q']),
    call('docker inspect $(docker ps -q)', shell=True)
  ])


def test_start_server(mock_subprocess):
  docker = Docker()
  docker.start_server(56, 0, '/test/gamesettings/path')

  mock_subprocess.call.assert_has_calls([
    call(['docker', 'rm', '-f', 'taserver_56']),
    call([
      'docker', 'run', '--name', 'taserver_56', 
      '-v', '/test/gamesettings/path:/gamesettings', 
      '-d', '--restart', 'unless-stopped', '--cap-add', 'NET_ADMIN',
      '-p', '7777:7777/tcp', '-p', '7777:7777/udp',
      '-p', '7778:7778/tcp', '-p', '7778:7778/udp',
      '-p', '9002:9002/tcp', '-p', '9002:9002/udp',
      'taserver', '--port-offset=0'
    ])
  ])


def test_start_server_offset(mock_subprocess):
  docker = Docker()
  docker.start_server(1234, 10, '/test/gamesettings/path')

  mock_subprocess.call.assert_has_calls([
    call(['docker', 'rm', '-f', 'taserver_1234']),
    call([
      'docker', 'run', '--name', 'taserver_1234', 
      '-v', '/test/gamesettings/path:/gamesettings', 
      '-d', '--restart', 'unless-stopped', '--cap-add', 'NET_ADMIN',
      '-p', '7787:7787/tcp', '-p', '7787:7787/udp',
      '-p', '7788:7788/tcp', '-p', '7788:7788/udp',
      '-p', '9012:9012/tcp', '-p', '9012:9012/udp',
      'taserver', '--port-offset=10'
    ])
  ])


def test_stop_server(mock_subprocess):
  docker = Docker()
  docker.stop_server(1234)
  mock_subprocess.call.assert_called_once_with(['docker', 'rm', '-f', 'taserver_1234'])

# test all the functionality of NullDocker
def test_null_docker(mock_subprocess):
  nd = NullDocker()
  assert {} == nd.status()
  nd.start_server(5, 0, "test")
  assert {5:0} == nd.status()

  nd.stop_server(4)
  assert {5:0} == nd.status()

  nd.stop_server(5)
  assert {} == nd.status()

  assert [] == mock_subprocess.method_calls
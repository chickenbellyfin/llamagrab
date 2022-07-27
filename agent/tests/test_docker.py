from unittest.mock import Mock, call

import pytest
from docker.errors import NotFound
from src.lib.docker import Docker, NullDocker


def make_object(**kwargs):
  return type('obj', (object,), kwargs)

@pytest.fixture
def mock_client():
  return Mock()

def test_status_empty(mock_client):
  mock_client.containers.list.return_value = []
  docker = Docker(mock_client)
  result = docker.status()
  assert {} == result


def test_status(mock_client):
  test1 = make_object(
    labels = {
      'llamagrab': '',
      'server_id': '111',
      'port_offset': '6'
    }
  )
  test2 = make_object(
    labels = {
      'llamagrab': '',
      'server_id': '222',
      'port_offset': '2'
    }
  )
  test3 = make_object( # not a taserver
    labels = {
      'server_id': '333',
      'port_offset': '0'
    }
  )
  mock_client.containers.list.return_value = [
    test1, test2, test3
  ]
  docker = Docker(mock_client)
  result = docker.status()
  assert {
    111: 6,
    222: 2
  } == result


def test_start_server(mock_client):
  docker = Docker(mock_client)

  docker.start_server(56, 0, '/test/gamesettings/path', '/test/banlist.txt')

  mock_client.assert_has_calls([
    call.containers.get('taserver_56'),
    call.containers.get().remove(force=True),
    call.containers.run(
      'taserver',
      command = ['--port-offset=0'],
      name = 'taserver_56',
      labels = {
        'llamagrab': '',
        'server_id': '56',
        'port_offset': '0'
      },
      volumes = [
        '/test/gamesettings/path:/gamesettings',
        '/test/banlist.txt:/app/taserver/data/banlist.txt'
      ],
      detach = True,
      restart_policy = {'Name': 'unless-stopped'},
      cap_add = ['NET_ADMIN'],
      ports = {
        '7777/tcp':7777,
        '7777/udp':7777,
        '7778/tcp':7778,
        '7778/udp':7778,
        '9002/tcp':9002,
        '9002/udp':9002,
      },
      environment = None,
      network_mode = None
    )
  ])

def test_start_server_no_existing(mock_client):
  """
  Attempting to stop existing server raises NotFound
  """
  mock_client.containers.get.side_effect = NotFound('test not found')
  docker = Docker(mock_client)
  docker.start_server(56, 0, '/test/gamesettings/path', '/test/banlist.txt')

  mock_client.assert_has_calls([
    call.containers.get('taserver_56'),
    # remove() not called
    call.containers.run(
      'taserver',
      command = ['--port-offset=0'],
      name = 'taserver_56',
      labels = {
        'llamagrab': '',
        'server_id': '56',
        'port_offset': '0'
      },
      volumes = [
        '/test/gamesettings/path:/gamesettings',
        '/test/banlist.txt:/app/taserver/data/banlist.txt'
      ],
      detach = True,
      restart_policy = {'Name': 'unless-stopped'},
      cap_add = ['NET_ADMIN'],
      ports = {
        '7777/tcp':7777,
        '7777/udp':7777,
        '7778/tcp':7778,
        '7778/udp':7778,
        '9002/tcp':9002,
        '9002/udp':9002,
      },
      environment = None,
      network_mode = None
    )
  ])


def test_start_server_offset(mock_client):
  docker = Docker(mock_client)
  docker.start_server(1234, 10, '/test/gamesettings/path', '/test/banlist.txt')

  mock_client.assert_has_calls([
    call.containers.get('taserver_1234'),
    call.containers.get().remove(force=True),
    call.containers.run(
      'taserver',
      command = ['--port-offset=10'],
      name = 'taserver_1234',
      labels = {
        'llamagrab': '',
        'server_id': '1234',
        'port_offset': '10'
      },
      volumes = [
        '/test/gamesettings/path:/gamesettings',
        '/test/banlist.txt:/app/taserver/data/banlist.txt'
      ],
      detach = True,
      restart_policy = {'Name': 'unless-stopped'},
      cap_add = ['NET_ADMIN'],
      ports = {
        '7787/tcp':7787,
        '7787/udp':7787,
        '7788/tcp':7788,
        '7788/udp':7788,
        '9012/tcp':9012,
        '9012/udp':9012,
      },
      environment = None,
      network_mode = None
    )
  ])

def test_start_server_host_network(mock_client):
  docker = Docker(mock_client, use_host_networking=True)
  docker.start_server(56, 0, '/test/gamesettings/path', '/test/banlist.txt')
  mock_client.assert_has_calls([
    call.containers.get('taserver_56'),
    call.containers.get().remove(force=True),
    call.containers.run(
      'taserver',
      command = ['--port-offset=0'],
      name = 'taserver_56',
      labels = {
        'llamagrab': '',
        'server_id': '56',
        'port_offset': '0'
      },
      volumes = [
        '/test/gamesettings/path:/gamesettings',
        '/test/banlist.txt:/app/taserver/data/banlist.txt'
      ],
      detach = True,
      restart_policy = {'Name': 'unless-stopped'},
      cap_add = ['NET_ADMIN'],
      ports = None,
      environment = None,
      network_mode = 'host'
    )
  ])

def test_start_server_custom_login(mock_client):
  docker = Docker(mock_client, loginserver='loginserver.test.local')
  docker.start_server(56, 0, '/test/gamesettings/path', '/test/banlist.txt')
  mock_client.assert_has_calls([
    call.containers.get('taserver_56'),
    call.containers.get().remove(force=True),
    call.containers.run(
      'taserver',
      command = ['--port-offset=0'],
      name = 'taserver_56',
      labels = {
        'llamagrab': '',
        'server_id': '56',
        'port_offset': '0'
      },
      volumes = [
        '/test/gamesettings/path:/gamesettings',
        '/test/banlist.txt:/app/taserver/data/banlist.txt'
      ],
      detach = True,
      restart_policy = {'Name': 'unless-stopped'},
      cap_add = ['NET_ADMIN'],
      ports = {
        '7777/tcp':7777,
        '7777/udp':7777,
        '7778/tcp':7778,
        '7778/udp':7778,
        '9002/tcp':9002,
        '9002/udp':9002,
      },
      environment = ['LOGINSERVER=loginserver.test.local'],
      network_mode = None
    )
  ])

def test_start_server_custom_image(mock_client):
  docker = Docker(mock_client, image='some.registry/taseZZrver')
  docker.start_server(56, 0, '/test/gamesettings/path', '/test/banlist.txt')

  mock_client.assert_has_calls([
    call.containers.get('taserver_56'),
    call.containers.get().remove(force=True),
    call.containers.run(
      'some.registry/taseZZrver',
      command = ['--port-offset=0'],
      name = 'taserver_56',
      labels = {
        'llamagrab': '',
        'server_id': '56',
        'port_offset': '0'
      },
      volumes = [
        '/test/gamesettings/path:/gamesettings',
        '/test/banlist.txt:/app/taserver/data/banlist.txt'
      ],
      detach = True,
      restart_policy = {'Name': 'unless-stopped'},
      cap_add = ['NET_ADMIN'],
      ports = {
        '7777/tcp':7777,
        '7777/udp':7777,
        '7778/tcp':7778,
        '7778/udp':7778,
        '9002/tcp':9002,
        '9002/udp':9002,
      },
      environment = None,
      network_mode = None
    )
  ])

def test_stop_server(mock_client):
  docker = Docker(mock_client)
  docker.stop_server(1234)
  mock_client.assert_has_calls([
    call.containers.get('taserver_1234'),
    call.containers.get().remove(force=True)
  ])

# test all the functionality of NullDocker
def test_null_docker():
  nd = NullDocker()
  assert {} == nd.status()
  nd.start_server(5, 0, "test")
  assert {5:0} == nd.status()

  nd.stop_server(4)
  assert {5:0} == nd.status()

  nd.stop_server(5)
  assert {} == nd.status()

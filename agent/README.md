# ServerManager Agent
ServerManager Agent - Service that runs on each host server. It listens for commands from ServerManager API and runs taserver docker containers on the host accordingly.

## Commands:
Commands are of the form:
```
{
  'type': str,
  'payload': Optional[str]
}
```
Agent responds to every command with `0` (int).

### sync
Sync message payloads contain the entire set of taserver configs which are suppost to run on the host.
```
{
  0: '<tamods lua config>',
  1: '<tamods lua config>',
  <serverid:int>: '<tamods lua config>',
  ...
}
```
Agent compares the incoming server list and config hashes with the previous saved active servers and running docker containers. It then kills, starts, and restarts containers to match the new configuration.

### ping
Empty payload, used for testing/status, has no effect.

## Run
```
python3 main.py <config.yaml>
```

#### Run unit tests
```
python3 -m pytest
```

#### Local testing server
For local testing without running actual taserver containers, make sure to add `testing: true` to config.yaml. This will disable the docker implementation with `NullDocker`

## Deployment
Copy agent/ dir to the host
```
$ rsync -vr agent $hostname:~
```

Run `setup.sh`. This will install docker, python+deps, and download the latest taserver docker image.
```
$ ssh $hostname
$ sudo agent/scripts/setup.sh
```

Setup and configure agent systemd service on the host:
```
$ cp agent/config.yaml .
$ nano config.yaml # add auth_key and disable testing mode

# Add systemd service
$ cp agent/scripts/smagent.service .
$ nano smagent.service # edit paths if needed
$ ln smagent.service /etc/systemd/system
$ sudo systemctl enable smagent && sudo systemctl start smagent

# Watch logs
$ journalctl -u smagent -f
```

### Configuration
port and auth_key must match on the taservermanager API config. Default port is 8999
config.yaml:
```
# all state / serverconfig lua will be stored here
gamesettings_dir: <path: str>
# auth key must match ServerManager API's auth_key
auth_key: <str>
port: <port: int>
```
Auth keys can be generated with `python3 -c 'import os; print(os.urandom(10).hex())'`

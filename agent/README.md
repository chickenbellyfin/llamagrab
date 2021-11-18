# ServerManager Agent
ServerManager Agent - Service runs on each host server. It listens for commands from ServerManager API and runs taserver docker containers on the host accordingly.

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
Sync messages contain the entire set of taserver configs which are suppost to run on the host. Agent compares the incoming server list with the previous saved active servers and running docker containers, then kills, starts, and restarts containers to match the new configuration.

### ping
Empty payload, used for testing, has no effect


## Setup
- docker must be installed and the taserver docker image must be pulled and tagged as `taserver`
- generate an auth_key with `python3 -c 'import os; print(os.urandom(10).hex())'`
- create a `config.yaml`:
  ```
  # all state / serverconfig lua will be stored here
  gamesettings_dir: <path: str>
  # auth key must match ServerManager API's auth_key
  auth_key: <str>
  port: <port: int>
  ```


## Run
```
python3 main.py <config.yaml>
```

## Test

#### Run unit tests
```
python3 -m unittest
```

#### Local testing server
For local testing without running actual taserver containers, add `testing: true` to config.yaml. This will disable the docker implementation with `NullDocker`

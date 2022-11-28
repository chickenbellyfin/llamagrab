# llamagrab-agent
LLamagrab Agent - Service that runs on each host server. It listens for commands from the API and runs taserver docker containers on the host accordingly.

## Agent Endpoints
All agent endpoins require a token header:

`Token: <token>`

### POST /api/sync
Sync message payloads contain the entire set of taserver configs which are suppost to run on the host.
```
{
  0: {
    'lua': '<tamods lua config>',
    'loginserver': '<optional:loginserver url>'
  },
  1: { ... },
  <serverid:int>: { ... },
  ...
}
```
Agent compares the incoming server list and config hashes with the previous saved active servers and running docker containers. It then kills, starts, and restarts containers to match the new configuration.

Responds with `ok`

### GET /api/status
Returns a list of server ids of containers which are currently running on the host.

Response with:
```
{
  0: 0,
  1: 2,
  <serverid:int>: <post_offset:int>,
  ...
}
```

### POST /api/ping
Empty payload, used for testing/status, has no effect. Response with `pong`

## Build
```
$ docker build . -t llamagrab-agent
```

## Run
Run locally
```
$ LG_TOKENS=test_token python3 -m src.main
```

Run docker container
```
$ docker run -v /var/run/docker.sock:/var/run/docker.sock -v /home/ubuntu/llamagrab_agent:/data -p 8999:8999 llamagrab-agent
```

Run with docker-compose
```
version: '3.6'

services:
  llamagrab-agent:
    image: r.llamagrab.net/llamagrab-agent
    container_name: llamagrab-agent
    volumes:
      - './llamagrab_agent:/data'
      - '/var/run/docker.sock:/var/run/docker.sock'
    environment:
      - LG_HOST_ABS_DATA_DIR=/home/azureuser/llamagrab_agent
      - LG_TASERVER_IMAGE=public.ecr.aws/i2q9d4v7/taserver
      - LG_TOKENS=a1b2c3d4e5f6
    restart: unless-stopped

  caddy:
    image: caddy
    container_name: caddy
    restart: unless-stopped
    ports:
      - 80:80
      - 443:443
      - 8999:8999
    volumes:
      - certs-volume:/data
    command: caddy reverse-proxy --from llamagrab.$REGION.cloudapp.azure.com:8999 --to llamagrab-agent:8999

volumes:
  certs-volume:

```

#### Run unit tests
```
python3 -m pytest
```

#### Local testing server
For local testing without running actual taserver containers, make sure to add `testing: true` to config.yaml. This will disable the docker implementation with `NullDocker`

## Configuration
Agent is configured through env vars

| ENV | Required? | Default | Description
| -- | -- | -- | -- |
| LG_HOST_ABS_DATA_DIR |  |  | If running in docker, should be the path on the host which will contain gamesettings 
| LG_PORT |  | `8999` | HTTP Port for the agent API. Must match the setting in llamagrab-api. 
| LG_TESTING | | `false` in docker image, `true` otherwise | Disables launching actual game servers and uses dummy implementation. This is set to `false` in the docker image.
| LG_LOGINSERVER | | | Override the loginserver that game servers connect to. By default, taserver-docker image uses `ta.kfk4ever.com`
| LG_USE_HOST_NETWORKING | | `false` | Set to `true` if loginserver is on the same host as taserver so that loginserver can detect the correct IP for taservers
| LG_TASERVER_IMAGE | | `taserver` | Docker image to launch for taserver.
| LG_TOKENS | **Required** | | Comma separated list of auth tokens which will allow API access.

## Auth Tokens
Agent uses a `Token` HTTP header to authenticate incoming api requests. At least one token must be set using the LG_TOKEN env and the same token should be provided to llamagrab-api to allow it to manage the agent instance.

`Token: <token>`

It is recommended to generate the tokens randomly:
```
python3 -c "import os; print(os.urandom(16).hex())"
```

## Deployment

Run `setup.sh`. This will install docker and download the latest taserver/agent docker image.


Create a docker-compose config and run it
```
$ nano ~/docker-compose.yaml
# (see example config above)

$ docker-compose up -d
```



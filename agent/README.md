# llamagrab-agent
LLamagrab Agent - Service that runs on each host server. It listens for commands from the API and runs taserver docker containers on the host accordingly.

## Commands:
Commands are of the form:
```
{
  'type': str,
  'payload': Optional[str]
}
```

### sync command
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

### status command
Returns a list of server ids of containers which are currently running on the host.

### ping command
Empty payload, used for testing/status, has no effect.

## Build
```
$ docker build . -t llamagrab-agent
```

## Run
Run locally
```
$ python3 -m src.main <config.yaml>
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
    image: public.ecr.aws/i2q9d4v7/llamagrab-agent
    container_name: llamagrab-agent
    volumes:
      - './llamagrab_agent:/data'
      - '/var/run/docker.sock:/var/run/docker.sock'
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

## Deployment

Run `setup.sh`. This will install docker and download the latest taserver/agent docker image.

Create a data dir:
```
$ mkdir llamagrab_agent
```

Create config.yaml in the data dir
```
$ nano llamagrab_agent/config.yaml

# Something like:
  host_abs_data_dir: /home/azureuser/llamagrab_agent
  port: 8999
  image: 'public.ecr.aws/i2q9d4v7/taserver'
  tokens:
    - <token> # generate a random token & add to llamagrab api's config
```

Create a docker-compose config and run it
```
$ nano ~/docker-compose.yaml
# (see example config above)

$ docker-compose up -d
```

### Configuration
See config.yaml for explanation of available settings.

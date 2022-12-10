# Llamagrab
![Unit Tests - API](https://github.com/chickenbellyfin/llamagrab/actions/workflows/pytest.yml/badge.svg)


## Tribes Ascend Community Server Manager

![](/docs/banner.png)

## Components
### Web
React Web UI for adding & configuring servers. The web UI will contain some permissions/validation logic for a better user experience, but should not be depended on to validate data or enforcing permissions.

For deployment, it is built as a static site and served by the API server from the api/static/ dir.

### API
Backend for the web UI, also handles user management. All validation/permissions are implemented/enforced in this layer.

Data is written to a local sqlite database.

Whenever a server config (including game settings,start,stop,delete) is changed, it triggers a `sync` with all of the hosts. A sync re-generates all of the lua scripts for all RUNNING servers and sends them to the respective agent instances on each host. Syncs are rate limited to every 30 seconds, but will be eventually consistent.

### Agent
Service which runs on each host server. Receives sync commands from API and schedules taserver instances using docker.

See [agent](/agent/README.md) for more details.

### Architecture Diagram
![diagram](/docs/architecture.drawio.png)

## Build
```
docker build . -t llamagrab -f api/Dockerfile
```

## Run
Minimal run command:
```
docker run -P llamagrab
```
The minimal command will store data inside the container, won't be able to keep host servers in sync, and only good for trying out the UI locally.

```
docker run -p 8000:8000 -v $(pwd)/data:/data llamagrab /data/config.yaml
```

## Development
For development, the API and the Web App need to be started. The agents are optional but can also be run in a local enviroment for testing.

All components will be able to commicate with each other on localhost without any configuration:

- local Web app is available at http://localhost:3000
- local API listens on localhost:8000
- local Agents listens on localhost:8999

### Start local API
```
pip install -r api/requirements.txt

python3 -m api
```

### Start local web app
```
cd web
yarn install

yarn start
```

### (Optional) Start local Agent
The local agent will stub out any calls to docker, so no game servers will actually be started.
```
pip install -r agent/requirements.txt

python3 -m agent
```

### Unit Tests
```
# tests for api + agent
$ python -m pytest

$ (cd web && yarn test --ci)

# Using coverage.py
$ coverage run && coverage report
```

## Release
Build for amd64 & arm64 & push to ECR
```
docker buildx build --platform linux/amd64,linux/arm64 --tag r.llamagrab.net/llamagrab -f api/Dockerfile --push .
```

## Production Deployment Setup
```
# first time setup
mkdir -p ~/data
touch ~/data/config.yaml # Must add config here before continuing

# use docker-compose
nano docker-compose.yaml

docker-compose pull && docker-compose up -d
```

#### docker-compose.yaml
```
version: '3.6'

services:
  llamagrab:
    image: r.llamagrab.net/llamagrab
    container_name: llamagrab
    volumes:
      - './data/llamagrab:/data'
    command: /data/config.yaml
    restart: unless-stopped
  
  # use caddy for HTTPS
  caddy:
    image: caddy
    container_name: caddy
    restart: unless-stopped
    ports:
      - 80:80
      - 443:443
    volumes:
      - ./data/Caddyfile:/etc/caddy/Caddyfile
      - certs-volume:/data

volumes:
  certs-volume:
```

Caddy is used as a reverse proxy and for automatically provisioning TLS certificates.

#### ./data/Caddyfile:
```
llamagrab.net {
  reverse_proxy llamagrab:8000
}
```
Open :80 and :443 in network security group/firewall

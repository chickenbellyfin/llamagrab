# Llamagrab
![Unit Tests - API](https://github.com/chickenbellyfin/llamagrab/actions/workflows/pytest_api.yml/badge.svg)
![Unit Tests - Agent](https://github.com/chickenbellyfin/llamagrab/actions/workflows/pytest_agent.yml/badge.svg)

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
docker build . -t llamagrab
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
cd api
pip install -r requirements.txt

python3 -m app
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
cd agent
python3 -m src.main
```

### Unit Tests
```
$ (cd api && python -m pytest)
$ (cd web && yarn test --ci)
$ (cd agent && python -m pytest)

# Using coverage.py in api/ or agent/ (run test & open in browser)
coverage run --source=src -m pytest && coverage html && xdg-open htmlcov/index.html
```

## Release
Build for amd64 & arm64 & push to ECR
```
docker buildx build --platform linux/amd64,linux/arm64 --tag public.ecr.aws/i2q9d4v7/llamagrab:latest --push .
```

## Production Deployment Setup
```
# first time setup
mkdir -p ~/data
touch ~/data/config.yaml # Must add config here before continuing

# download/update image
docker pull public.ecr.aws/i2q9d4v7/llamagrab:latest

# kill existing container and start new one
docker rm -f llamagrab-app
docker run --name llamagrab-app -d --restart unless-stopped -p 8000:8000 -v "$data_path:/data" public.ecr.aws/i2q9d4v7/llamagrab:latest "/data/config.yaml"

# or

docker-compose pull && docker-compose up -d
```

#### docker-compose.yaml
```
version: '3.6'

services:
  llamagrab:
    image: public.ecr.aws/i2q9d4v7/llamagrab
    container_name: llamagrab-app
    volumes:
      - './data/llamagrab:/data'
    ports:
      - 8000:8000
    command: /data/config.yaml
    restart: unless-stopped
```

Caddy is used as a reverse proxy and for automatically provisioning TLS certificates.

#### /etc/caddy/Caddyfile:
```
llamagrab.net {
  reverse_proxy localhost:8000
}
```
Open :80 and :443 in network security group/firewall

# Tribes Server Manager

## Components
- insert diagram

## Build
```
docker build . -t taservermanager
```

build for amd64 & arm64
```
docker buildx build --platform linux/amd64,linux/arm64 --tag public.ecr.aws/i2q9d4v7/taservermanager:latest --push .
```


## Run
Minimal run command:
```
docker run -P taservermanager
```
The minimal command will store data inside the container, won't be able to keep host servers in sync, and only good for trying out the UI locally.

```
docker run -p 8000:8000 -v $(pwd)/data:/data taservermanager /data/config.yaml 
```

## Development Setup
For development, the API and the Web App need to be started. The agents are optional but can also be run in a local enviroment for testing.

All components will be able to commicate with each other on localhost without any configuration:

- local Web app is available at http://localhost:3000
- local API listens on localhost:8000
- local Agents listens on localhost:8999

### Start local API
```
cd api
pip install -r requirements.txt

python3 app.py
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
python3 agent.py
```

### Unit Tests
```
cd api
python3 -m pytest --full-trace

# Using coverage.py (run test & open in browser)
coverage run --source=. -m pytest && coverage html && xdg-open htmlcov/index.html
```

## Production Deployment Setup

```
# first time setup
mkdir -p ~/data
touch ~/data/config.yaml # Must add config here before continuing

# download/update image
docker pull public.ecr.aws/i2q9d4v7/taservermanager:latest
docker tag public.ecr.aws/i2q9d4v7/taservermanager:latest taservermanager

docker run --name taservermanager -d --restart unless-stopped -p 8000:8000 -v "$data_path:/data" taservermanager "/data/config.yaml" 
```


Caddyfile:
```
servers.llamagrab.net {
  reverse_proxy localhost:8000
}
```

Open :80 and :443 in network security group/firewall



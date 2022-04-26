#!/bin/bash
set -ex

# Install docker & docker-compose
# https://docs.docker.com/engine/install/ubuntu/#install-using-the-convenience-script
if [ -z $(which docker) ]; then
  curl -L "https://get.docker.com" -o "get-docker.sh"
  sudo sh get-docker.sh && rm get-docker.sh
  # setup current user for docker
  sudo usermod -aG docker $USER
  newgrp docker
  sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
else
  echo "Docker is already installed, skipping"
fi

# get taserver image
docker pull public.ecr.aws/i2q9d4v7/llamagrab-agent
docker pull public.ecr.aws/i2q9d4v7/taserver


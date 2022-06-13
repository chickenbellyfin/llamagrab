#!/bin/bash
set -ex

# Install docker
# https://docs.docker.com/engine/install/ubuntu/#install-using-the-convenience-script
if [ -z "$(which docker)" ]; then
  curl -L "https://get.docker.com" -o "get-docker.sh"
  sudo sh get-docker.sh && rm get-docker.sh
  # setup current user for docker
  sudo usermod -aG docker "$USER"
else
  echo "Docker is already installed, skipping"
fi

# Install docker-compose
sudo apt update && sudo apt install python3-pip -y
sudo pip install docker-compose

newgrp docker <<'EOF'
# get taserver image
docker pull public.ecr.aws/i2q9d4v7/llamagrab-agent
docker pull public.ecr.aws/i2q9d4v7/taserver
EOF

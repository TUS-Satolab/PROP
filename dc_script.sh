#!/bin/sh

BACKEND_ONLY=0
FRONTEND_ONLY=0
# Loop through arguments and process them
for arg in "$@"
do
    case $arg in
        --backend-only)
        BACKEND_ONLY=1
        shift # Remove --backend-only from processing
        ;;
        --frontend-only)
        FRONTEND_ONLY=1
        shift # Remove --frontend-only from processing
        ;;
    esac
done

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found"
    exit 1
fi

# Extract APIKEY from .env file
APIKEY=$(grep '^BACKEND_APIKEY=' .env | awk -F '=' '{print $2}')

# Check if APIKEY was successfully extracted
if [ -z "$APIKEY" ]; then
    echo "Error: BACKEND_APIKEY not found in .env file"
    exit 1
fi

if [ "$FRONTEND_ONLY" = "1" ] && [ "$BACKEND_ONLY" = "1" ]
then
  echo "Can't set both --frontend-only and --backend-only at the same time"
  exit 1
fi

# ----------------------------
# Creation of backend
# ----------------------------
if [ "$FRONTEND_ONLY" = "0" ]
  then
cat <<EOF >./.dockerignore
.git
.cache
node_modules
.gitignore
frontend
EOF

# delete Docker volume to force rebuilding
echo "Stopping backend containers"
docker container stop $(docker container ls -q --filter name=prop_backend_)
echo "Deleting backend containers"
docker rm $(docker container ls -a -q --filter name=prop_backend_)
echo "Deleting backend images"
docker rmi $(docker images -q --filter=reference='prop_backend_*:*')
echo "Deleting Docker volume"
docker volume rm prop_docker_volume
echo "Pruning leftover Docker layers and caches"
docker system prune -a --force
# for old build method: DOCKER_BUILDKIT=0 
docker compose -f compose.yml up -d --build

rm .dockerignore
else
  echo "Only creating frontend"
fi
# ----------------------------
# Creation of frontend locally
# ----------------------------
if [ "$BACKEND_ONLY" = "0" ]
  then
  echo "Creating Frontend"
  cat <<EOF >./.dockerignore
.git
.cache
.gitignore
requests
frontend/node_modules
EOF

  cd frontend
  npm install
  cd ..
  echo "Stopping frontend container"
  docker container stop $(docker container ls -q --filter name=prop_frontend)
  echo "Deleting frontend container"
  docker rm $(docker container ls -a -q --filter name=prop_frontend)
  echo "Deleting frontend image"
  docker rmi $(docker images -q --filter=reference='prop_frontend:*')
  # for old build method: DOCKER_BUILDKIT=0 
  docker compose -f compose-angular.yml up -d --build
  rm .dockerignore
else
  echo "Only created backend"
fi

#!/bin/sh

# Necessary to work for both OSX and Linux
SEDOPTION=
if [[ "$OSTYPE" == "darwin"* ]]; then
  SEDOPTION="-i ''"
fi

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
IP_ADDRESS="$(dig +short myip.opendns.com @resolver1.opendns.com)"
# ----------------------------
# Creation of backend
# ----------------------------
grep -q '^IP_ADDRESS' .env && sed $SEDOPTION -e "s/^IP_ADDRESS.*$/IP_ADDRESS=${IP_ADDRESS}/g" .env || echo "IP_ADDRESS=$IP_ADDRESS" >> .env
APIKEY="$(echo "$NAME" | grep 'BACKEND_APIKEY=' .env | sed 's/^.*=//')"
cat >./frontend/src/app/env.json <<EOF 
{
  "env": [
              {"id":1,"ip_address":"$IP_ADDRESS"},
              {"id":2,"local_flag":"1"},
              {"id":3,"apikey":"$APIKEY"}
   ]
}
EOF

if [[ $FRONTEND_ONLY -eq 1 && $BACKEND_ONLY -eq 1  ]]
then
  echo "Can't set both --frontend-only and --backend-only at the same time"
  exit 1
fi

if [[ $FRONTEND_ONLY -eq 0 ]]
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
docker-compose -f docker-compose.yml up -d --build

rm .dockerignore
else
  echo "Only creating frontend"
fi
# ----------------------------
# Creation of frontend locally
# ----------------------------
if [[ $BACKEND_ONLY -eq 0 ]]
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
  docker-compose -f docker-compose-angular.yml up -d --build
  rm .dockerignore
else
  echo "Only created backend"
fi
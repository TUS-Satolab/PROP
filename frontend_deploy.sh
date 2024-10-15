#!/bin/sh

IP_ADDRESS=$1
echo "IP_ADDRESS=$IP_ADDRESS" > .env
APIKEY="$(echo "$NAME" | grep 'BACKEND_APIKEY=' .env | sed 's/^.*=//' 
cat >./frontend/src/app/env.json <<EOF 
{
  "IP_ADDRESS": "$IP_ADDRESS",
  "LOCAL_FLAG": "1",
  "APIKEY": "$APIKEY",
  "FILE_SIZE_LIMIT": "$FILE_SIZE_LIMIT"
}
EOF
echo "LOG: Creating dockerignore file"
cat <<EOF >./.dockerignore
.git
.cache
.gitignore
requests
frontend/node_modules
EOF

cd frontend
echo "LOG: Installing packages"
npm install
echo "LOG: Finished installing packages"
cd ..
echo "LOG: Running docker　compose"
docker compose -f compose-angular.yml up -d
echo "LOG: Finished docker compose"
rm .dockerignore
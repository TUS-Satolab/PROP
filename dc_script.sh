#!/bin/sh

IP_ADDRESS="$(dig +short myip.opendns.com @resolver1.opendns.com)"
# ----------------------------
# Creation of backend
# ----------------------------
grep -q '^IP_ADDRESS' .env && sed -i '' -e "s/^IP_ADDRESS.*$/IP_ADDRESS=${IP_ADDRESS}/g" .env || echo "IP_ADDRESS=$IP_ADDRESS" >> .env
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

cat <<EOF >./.dockerignore
.git
.cache
node_modules
.gitignore
frontend
EOF

docker-compose -f docker-compose.yml up -d --build

rm .dockerignore
# ----------------------------
# Creation of frontend locally
# ----------------------------
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
docker-compose -f docker-compose-angular.yml up -d --build
rm .dockerignore

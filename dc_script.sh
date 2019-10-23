#!/bin/sh

IP_ADDRESS="$(dig +short myip.opendns.com @resolver1.opendns.com)"
echo "IP_ADDRESS=$IP_ADDRESS" > .env
cat >./frontend/src/app/env.json <<EOF 
{
  "ENV": [
              {"id":1,"ip_address":"$IP_ADDRESS"}
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
cat <<EOF >./.dockerignore
.git
.cache
.gitignore
requests
frontend/node_modules
EOF

docker-compose -f docker-compose-angular.yml up -d --build
rm .dockerignore
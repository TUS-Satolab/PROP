#!/bin/sh

IP_ADDRESS=$1
echo "IP_ADDRESS=$IP_ADDRESS" > .env
cat >./frontend/src/app/env.json <<EOF 
{
  "env": [
              {"id":1,"ip_address":"$IP_ADDRESS"},
              {"id":2,"local_flag":"2"}
   ]
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
echo "LOG: Running docker-compose"
docker-compose -f docker-compose-angular.yml up -d
echo "LOG: Finished docker-compose"
rm .dockerignore
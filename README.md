# canal_project

## Prerequisites
- Docker & docker-compose
  - https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04
  - https://www.digitalocean.com/community/tutorials/how-to-install-docker-compose-on-ubuntu-18-04
- npm
  - `curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -`
  - `sudo apt install nodejs`

## Installation
1. Pull this repo
2. `cd canal_project`
3. `cd frontend`
4. `sudo npm install`
5. `cd ..` (so that you are in folder canal_project again)
6. `sudo ./dc_script.sh 1` (for local environment) or `sudo ./dc_script.sh 2` (for server environment)

## Usage via browser
 If local environment: 
   - `http://localhost:5004/`    
   
If server environment:
   - Get the IP address of the server instance --> IP_ADDRESS
   - `[IP_ADDRESS]:5004`

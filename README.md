# canal_project

## Prerequisites

- Docker

## Installation Backend

1. Pull this repo
2. `cd canal_project`
3. `sudo ./dc_script.sh 1` (for local environment) or `sudo ./dc_script.sh 2` (for server environment)

## Installation Frontend

1. Pull this repo
2. `cd canal_project`
3. `cd frontend`
4. `sudo npm install`
5. open `node_modules/phylotree/src/cli/phylotree.js`  
   5.1 Delete the first line: `#!/usr/bin/env node`
6. go to folder `frontend/src/app`
7. rename `env_Dummy.json` to `env.json`
8. Replace the ip address of the backend server in the line with `id:1`
9. `cd ../..` (so that you are in the folder `frontend`)
10. `ng build --prod`

## Usage via browser

If local environment:

- `http://localhost:5004/`

If server environment:

- Get the IP address of the server instance --> IP_ADDRESS
- `[IP_ADDRESS]:5004`

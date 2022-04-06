# P\*R\*O\*P

## Prerequisites

- Docker & docker-compose
  - https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04
  - https://www.digitalocean.com/community/tutorials/how-to-install-docker-compose-on-ubuntu-18-04
- npm
  - `curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -`
  - `sudo apt install nodejs`

## Installation 
### Backend

1. Pull this repo
2. `cd PROP`
3. `sudo ./dc_script.sh`
Optional
4. Delete Angular Frontend Docker container if debugging is not needed.
```
  docker stop prop_frontend_1
  docker rm prop_frontend_1
```  

### Frontend (static)

1. Pull this repo
2. `cd PROP`
3. `cd frontend`
4. `sudo npm install`
5. copy/paste `frontend/src/app/envDummy.json` to `frontend/src/app/env.json`
6. In `frontend/src/app/env.json`, set `"local_flag":"2"` --> in that case, API Gateway endpoint is used instead of localhost
7. `cd ../..` (so that you are in the folder `frontend`)
8. `npx ng build --prod --output-path ../docs --base-href /bioinformatics/prop/`
9. In `frontend/src/app/header/header.component.html` change `src="/assets/canal_logo.svg"` to `src="/bioinformatics/prop/assets/canal_logo.svg"`
    
10. open `header.component.html`
   - Change from `../../assets/canal_logo.svg` to `/bioinformatics/prop/assets/canal_logo.svg`

11. Host the docs folder on a hosting platform

### local debugging

1. Pull this repo
2. `cd PROP`
3. copy/paste `frontend/src/app/envDummy.json` to `frontend/src/app/env.json`
4. create .env with `BACKEND_APIKEY=DUMMY`
4. `sudo ./dc_script.sh`
5. wait for the script to finish
6. open the website on `https://localhost:4200/`

## How to update 
### MAFFT / ClustalW variables
- array length and count variables can be set in `./.env.fixedVariables`
  - can set:
    - MAFFT array length & count
    - ClustalW array length & count
### frontend only
1. `sudo ./dc_script.sh --frontend-only`

### backend only
1. `sudo ./dc_script.sh --backend-only`

### re-build / update everything 
1. Rebuild: `sudo ./dc_script.sh`

## Usage via browser

- local environment: `https://localhost:4200/`

- static hosting: domain provided by the hosting platform


This software is released under the MIT License, see LICENSE.txt.

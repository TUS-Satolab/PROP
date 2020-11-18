# P\*R\*O\*P

## Prerequisites

- Docker & docker-compose
  - https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04
  - https://www.digitalocean.com/community/tutorials/how-to-install-docker-compose-on-ubuntu-18-04
- npm
  - `curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -`
  - `sudo apt install nodejs`

## Installation Backend (with debugging UI)

1. Pull this repo
2. `cd canal_project`
3. `sudo ./dc_script.sh 1`
4. write down the IP address of the server instance
Optional
5. Delete Angular Frontend Docker container if debugging is not needed.
```
  docker stop canal_project_angular-service_1
  docker rm canal_project_angular-service_1
```  
- For debugging: open the website on `localhost:4200/`

## Installation Frontend (static)

1. Pull this repo
2. `cd canal_project`
3. `cd frontend`
4. `sudo npm install`
5. copy/paste `frontend/src/app/envDummy.json` to `frontend/src/app/env.json`
6. make sure that in `frontend/src/app/env.json` `local_flag=2`
7. `cd ../..` (so that you are in the folder `frontend`)
8. `npx ng build --prod --output-path ../docs --base-href /bioinformatics/prop/`
9. In `frontend/src/app/header/header.component.html` change `src="/assets/canal_logo.svg"` to `src="/bioinformatics/prop/assets/canal_logo.svg"`
    
10. open `header.component.html`
   - Change from `../../assets/canal_logo.svg` to `/bioinformatics/prop/assets/canal_logo.svg`

11. Host the docs folder on a hosting platform

## Usage via browser

If local environment:

- `http://localhost:5004/`

If server environment (Docker):

- Get the IP address of the server instance --> IP_ADDRESS
- `[IP_ADDRESS]:5004`

If static hosting:

- use the domain provided by the hosting platform


This software is released under the MIT License, see LICENSE.txt.

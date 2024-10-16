# P\*R\*O\*P

## Prerequisites

- Docker & docker compose
  - https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04
  - https://www.digitalocean.com/community/tutorials/how-to-install-docker-compose-on-ubuntu-18-04
- npm
  - `curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -`
  - `sudo apt install nodejs`

## Development 
### Frontend & Backend

1. Pull this repo
2. `cd PROP`
3. create `.env` file with `BACKEND_APIKEY=DUMMY`
4. `sudo ./dc_script.sh`
5. wait for the script to finish
6. open the website on `https://localhost:4200/`
7. make changes to the frontend/backend code. Hot reload is enabled

NOTE:
- If you want to run the frontend/backend separately, you can do so by running `sudo ./dc_script.sh --frontend-only` or `sudo ./dc_script.sh --backend-only`

## Production
### Build
#### Frontend (static)

1. Pull this repo
2. `cd PROP`
3. `cd frontend`
4. `npm install`
5. copy/paste `frontend/src/app/envDummy.json` to `frontend/src/app/env.json`
6. In `frontend/src/app/env.json`, set `"local_flag":"2"` --> in that case, API Gateway endpoint is used instead of localhost
7. `cd ../..` (so that you are in the folder `frontend`)
8. open `header.component.html`
   - change `src="/assets/canal_logo.svg"` to `src="/bioinformatics/prop/assets/canal_logo.svg"`
9. `npm run build:prod`
10. Host the resulting `/docs` folder on a hosting platform

#### Backend

1. Pull this repo
2. `aws sso login --profile [PROFILE]` (if not already logged in)
3. make sure that `.env` file contains `AWS_ACCOUNT_ID` and `AWS_REGION`
4. `cd PROP`
5. `./build_and_upload.sh`
6. wait for the script to finish

NOTE:
- the script builds the Docker images and uploads them to AWS ECR repositories
  - access to that repository / AWS account is required


### Deploy
#### Frontend

1. Host the `docs` folder created during the build process on a hosting platform

#### Backend

1. SSH into the EC2 instance via the management console
   1. access to the EC2 instance / AWS account is required
2. copy `compose_deploy.yml` to the instance
3. ensure the `.env` file is present and contains the following variables:
   - `AWS_ACCOUNT_ID`
   - `AWS_REGION`
   - `BACKEND_APIKEY`
   - `MAFFT_ARRAY_COUNT` --> found in `./.env.fixedVariables`
   - `MAFFT_ARRAY_LENGTH` --> found in `./.env.fixedVariables`
   - `CLUSTALW_ARRAY_COUNT` --> found in `./.env.fixedVariables`
   - `CLUSTALW_ARRAY_LENGTH` --> found in `./.env.fixedVariables`
   - `NO_ALIGNMENT_ARRAY_COUNT` --> found in `./.env.fixedVariables`
   - `NO_ALIGNMENT_ARRAY_LENGTH` --> found in `./.env.fixedVariables`
   - `FILE_SIZE_LIMIT` --> found in `./.env.fixedVariables`
4. `docker compose -f compose_deploy.yml up -d`

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

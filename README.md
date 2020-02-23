# canal_project

## Prerequisites
- Docker

## Installation
1. Pull this repo
2. `cd canal_project`
3. `./dc_script.sh 1` (for local environment) or `./dc_script.sh 2` (for server environment)

## Usage via browser
1. Get the IP address of the server where the docker containers are running   
   If it's locally: `http://localhost:4200/`
2. In your browser input: [IP-address]:5004
   E.g. 

## Run the program locally
(0.) program help page access:   
   `python3 calculation.py -help`
   ```
   Usage:
  calculation.py [--input_file <input_file>] [--type <type>] [--align <align>]
                 [--align_clw_opt <align_clw_opt>] [--model <model>]
                 [--plusgap <plusgap>] [--gapdel <gapdel>] [--tree <tree>]

Options:
  -h --help                         Show this screen.
  --input_file=<input_file>             aln-file
  --type=<type>                     nuc or ami
  --align=<align>                   clustalw, mafft or none
  --align_clw_opt=<align_clw_opt>   string of options [default: ]
  --model=<model>                   P, PC, JS or K2P
  --plusgap=<plusgap>               "checked" / "" [default: ]
  --gapdel=<gapdel>                 "comp" / "pair" 
  --tree=<tree>                     "nj" / "upgma"
   ```
1. Example:  
   `python3 calculation.py --input_file unaligned.fasta --type nuc --align clustalw --model P --plusgap checked --gapdel comp --tree nj`
  
## Run the program with flask - CURRENTLY NOT WORKING
1. In the folder canal_project: `source venv/bin/activate`
2. flask run --host=0.0.0.0   

## Query the program remotely (e.g. [Postman](https://www.getpostman.com))
### 1. Alignment
1. Set `POST` and http://52.198.155.126:5000/alignment
2. Select `Body` and `form-data`
3. input 
   - file
   - align_method: `clustalw` or `mafft`
   - input_type: `nuc` or `ami`
   - align_clw_opt: [users who need that, know what to input. I don't know.]
4. `Send`
5. Result is:
   - input filename
   - jobID
   - output filename

### 2. Distance Matrix
1. Set `POST` and http://52.198.155.126:5000/matrix
2. Select `Body` and `form-data`
3. input 
   - file: Upload file OR select task_id
   - task_id: [previously received via Alignment command]
   - plusgap: `checked` or none
   - gapdel: `comp` or `pair`
   - input_type: `nuc` or `ami`
   - model: P, PC, JS or K2P
4. `Send`
5. Result is:
   - input filename
   - jobID
   - output filename
   
### 3. Tree
1. Set `POST` and http://52.198.155.126:5000/tree
2. Select `Body` and `form-data`
3. input 
   - score: Upload file OR select task_id
   - otus: Upload file OR select task_id
   - task_id: [previously received via Alignment command]
   - tree: `nj` or `upgma`
4. `Send`
5. Result is:
   - input filename otus
   - input filename score
   - jobID
   - output filename

### 4. Complete calculation
1. Set `POST` and http://52.198.155.126:5000/complete
2. Select `Body` and `form-data`
3. input 
   - file
   - align_method: `clustalw` or `mafft`
   - input_type: `nuc` or `ami`
   - align_clw_opt: [users who need that, know what to input. I don't know.]
   - plusgap: `checked` or none
   - gapdel: `comp` or `pair`
   - model: P, PC, JS or K2P
   - tree: `nj` or `upgma`
4. `Send`
5. Result is:
   - task_id
   
### 5. Get result
1. Set `POST` and http://52.198.155.126:5000/get_result
2. Select `Body` and `form-data`
3. input 
   - result_id: [previously received via Alignment command]
4. `Send`
5. Result is:
   - zip file with all files containing the `result_id`
   

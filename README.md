# canal_project

## Prerequisites
- Docker
- Python3 & pip

## Installation
1. Pull this repo
2. `docker build -f Dockerfile_clustalw -t my_clustalw .`
3. `docker build -f Dockerfile_mafft -t my_mafft .`
4. Install virtual environment   
   ```
   python3 -m venv venv
   source venv/bin/activate
   python3 -m pip install -r requirements.txt
   ``` 
5. `python3 -m pip install -r requirements.txt`

## Run the program
(0.) program help page access:   
   `python3 calculation.py -help`
   ```
   Usage:
  calculation.py [--filename <filename>] [--type <type>] [--align <align>]
                 [--align_clw_opt <align_clw_opt>] [--model <model>]
                 [--plusgap <plusgap>] [--gapdel <gapdel>] [--tree <tree>]

Options:
  -h --help                         Show this screen.
  --filename=<filename>             aln-file
  --type=<type>                     nuc or ami
  --align=<align>                   clustalw, mafft or none
  --align_clw_opt=<align_clw_opt>   string of options [default: ]
  --model=<model>                   P, PC, JS or K2P
  --plusgap=<plusgap>               "checked" / "" [default: ]
  --gapdel=<gapdel>                 "comp" / "pair" 
  --tree=<tree>                     "nj" / "upgma"

   ```
1. Example:  
   `python3 calculation.py --filename unaligned.fasta --type nuc --align clustalw --model P --plusgap checked --gapdel comp --tree nj`

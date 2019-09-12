# canal_project

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
6. Run the program help page with   
   `python3 calculation.py -help`
7. Example  
   `python3 calculation.py --filename unaligned.fasta --type nuc --align clustalw --model P --plusgap checked --gapdel comp --tree nj`

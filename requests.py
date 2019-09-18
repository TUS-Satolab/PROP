from flask import Flask
from calculation import alignment
import datetime, time, os

app = Flask(__name__)

@app.route('/post/alignment')
def align_flask():
    timestamp = datetime.datetime.today().strftime("%Y-%m-%d-%H-%M-%S")
    out_align = timestamp + "align.txt"
    #--filename small.fasta --type nuc --align clustalw --model P --gapdel comp --tree nj
    alignment(out_align, filename="small.fasta", d="DNA", align="clustalw", align_clw_opt="")
    return 'Finished alignment'
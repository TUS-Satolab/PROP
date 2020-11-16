"""
calculation

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
  --model=<model>                   P, PC, JC or K2P
  --plusgap=<plusgap>               "checked" / "not_checked" [default: not_checked]
  --gapdel=<gapdel>                 "comp" / "pair" 
  --tree=<tree>                     "nj" / "upgma"
"""

import datetime, time, shutil, sys, os, Bio, math, pickle, requests
import docker
#import re
#import subprocess 

from docopt import docopt
from flask import Flask, render_template, request
from Bio import Phylo, SeqIO
from Bio.Phylo import BaseTree
client = docker.from_env()
RESULT_FOLDER = "./files"
def complete_calc(out_align, filename, input_type, align_method, 
    align_clw_opt, matrix_output, gapdel, model, 
    tree, UPLOAD_FOLDER, out_tree, plusgap_checked):
    with open(os.path.join(RESULT_FOLDER, filename), 'r') as infile:
        data = infile.read()
        data_split = data.split(">")
        data_first_block = data_split[1][data_split[1].index('\n')+1:]
        data_first_block_stripped = data_first_block.replace('\n','')
        #data = infile.readlines()
        count_n = 0
        for i in data:
                if i.startswith(">"):
                    count_n += 1
    # If nucleotide, the length within a block is allowed to be below 900 and 10k total blocks
    if align_method == 'mafft' and (len(data_first_block_stripped) > 3000 or count_n > 3000):
        raise Exception("Linecount maximum exceeded")
    # If protein, the length within a block is allowed to be below 300 and 10k total blocks
    elif align_method == 'clustalw' and (len(data_first_block_stripped) > 3000 or count_n > 1000):
        raise Exception("Linecount maximum exceeded")
    elif align_method == 'None' and (len(data_first_block_stripped) > 3000 or count_n > 3000):
        raise Exception("Linecount maximum exceeded")
        
    alignment(out_align, filename, input_type, align_method, align_clw_opt)
    (score, otus) = distance_matrix(out_align, matrix_output, gapdel, input_type, model, plusgap_checked)            
    phylo_tree(score, otus, tree, UPLOAD_FOLDER, out_tree)



def main(args):
    #get timestamp
    start = time.time()
    timestamp = datetime.datetime.today().strftime("%Y-%m-%d-%H-%M-%S")
    out_align = timestamp + "alignment.txt"
    matrix_output = timestamp + "matrix.txt"
    out_tree = timestamp + "tree.txt"
    ############ docopt arguments ###############
    input_file = args["--input_file"]
    input_type = args["--type"]
    if input_type not in ["nuc", "ami"]:
        raise Exception("Data type is neither nuc nor ami")
    align = args["--align"]
    align_clw_opt = args["--align_clw_opt"]
    
    model = args["--model"]
    plusgap = args["--plusgap"]
    gapdel = args["--gapdel"]
    tree = args["--tree"]
    UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "/files"
    # Start a Docker instance and output an aligned file
    alignment(out_align, input_file, input_type, align, align_clw_opt)


    (score, otus) = distance_matrix(out_align, matrix_output, gapdel, input_type, model, plusgap)

    phylo_tree(score, otus, tree, out_tree=out_tree)
    
    #get result
    f = open(os.path.join(RESULT_FOLDER, out_align))
    align_result = f.read()
    f.close()
    f = open(os.path.join(RESULT_FOLDER, matrix_output))
    matrix_result = f.read()
    f.close()
    f = open(os.path.join(RESULT_FOLDER, out_tree))
    tree_result = f.read()
    f.close()

    return ["Complete.",align_result.replace("\n","NEWLINE"),matrix_result.replace("\n","NEWLINE"),tree_result.replace("\n","NEWLINE")]

def alignment(out_align, input_file, input_type, align=None,  align_clw_opt=None):
    with open(os.path.join(RESULT_FOLDER, input_file), 'r') as infile:
        data = infile.read()
        data_split = data.split(">")
        data_first_block = data_split[1][data_split[1].index('\n')+1:]
        data_first_block_stripped = data_first_block.replace('\n','')
        #data = infile.readlines()
        count_n = 0
        for i in data:
                if i.startswith(">"):
                    count_n += 1
    # If nucleotide, the length within a block is allowed to be below 900 and 10k total blocks
    if align == 'mafft' and (len(data_first_block_stripped) > 3000 or count_n > 3000):
        raise Exception("Linecount maximum exceeded")
    # If protein, the length within a block is allowed to be below 300 and 10k total blocks
    elif align == 'clustalw' and (len(data_first_block_stripped) > 3000 or count_n > 1000):
        raise Exception("Linecount maximum exceeded")
    elif align == 'None' and (len(data_first_block_stripped) > 3000 or count_n > 3000):
        raise Exception("Linecount maximum exceeded")

    input_type_dict = {"nuc": "DNA", "ami": "PROTEIN"}
    d = input_type_dict[input_type]
    # d is either DNA or PROTEIN
    if align == "None":
        pass
        # shutil.copy(input_file, out_align)
    elif align == "clustalw":
        try:
            client.containers.run(image="my_clustalw", command="clustalw -INFILE="+ RESULT_FOLDER +input_file+ \
                                " -OUTFILE=" + RESULT_FOLDER + out_align + " -OUTPUT=PIR -OUTORDER=INPUT -TYPE=" \
                                + d + " " + align_clw_opt, \
                                volumes={'canal_project': {'bind': '/data', 'mode': 'rw'}},remove=True)
        except Exception as e:
            raise Exception("Alignment error", e)
    elif align == "mafft":
        try:
            client.containers.run(image="my_mafft", command="bash -c 'mafft " + "files/" + input_file + \
                                " > files/" + out_align + "'", \
                                volumes={'canal_project': {'bind': '/data', 'mode': 'rw'}},remove=True)
        except Exception as e: 
            raise Exception("Alignment error", e)
    else:
        raise Exception("Check datatype or align definitions")
    print("Created alignment file")

#################################################################################
# INPUTS: out_align, matrix_output, plusgap, gapdel, input_type, model
# OUTPUTS: score, otus, matrix_output
#################################################################################
def distance_matrix(aligned_input, matrix_output, gapdel, input_type, model, plusgap):

    # with open(os.path.join('./files', aligned_input), 'r') as infile:
    #     data = infile.read()
    #     data_split = data.split(">")
    #     data_first_block = data_split[1][data_split[1].index('\n')+1:]
    #     data_first_block_stripped = data_first_block.replace('\n','')
    #     #data = infile.readlines()
    #     count_n = 0
    #     for i in data:
    #             if i.startswith(">"):
    #                 count_n += 1
    # # the length within a block is allowed to be below 900 and 10k total blocks
    # if len(data_first_block_stripped) > 3000 or count_n > 3000:
    #     raise Exception("Linecount maximum exceeded")


    # TODO: is it correct to input the aligned file? Get error otherwise
    print("Filename is:", aligned_input)
    (otus, seqs) = parse_otus(aligned_input) 
    #Complete Deletion Option
    if plusgap == "not_checked" and gapdel == "comp":
        # for i in range(len(seqs[0])):
        #     for j in range(len(otus)):
        #         if seqs[j][i] == "-":
        #             for k in range(len(otus)):
        #                 tmp = list(seqs[k])
        #                 tmp[i] = "-"
        #                 seqs[k] = "".join(tmp)

        dropnum=[]
        for s in seqs:
            dropnum += [i for i in range(len(s)) if s[i] == "-"]   
        droplist = list(set(dropnum))
        droplist.sort(reverse=True)
        
        for d in droplist:
            for i in range(len(seqs)):
                seqs[i] = "".join(seqs[i][:d])+"".join(seqs[i][d+1:])
    

    #Create distance matrix
    print("Create Distance Matrix...")
    function_mapping = {
        'nuc': 'calcDiff_nuc',
        'ami': 'calcDiff_ami'
    }
    matrix_func = globals()[function_mapping[input_type]]
    #score = function_mapping[input_type](model,plusgap,seqs,len(otus))
    #if input_type == "nuc":
    score = matrix_func(model,plusgap,seqs,len(otus))
        #score = calcDiff(model,plusgap,seqs,len(otus))
    #elif input_type == "ami":
        #score = matrix_func(model,plusgap,seqs,len(otus))
        #score = calcDiffProtein(model,plusgap,seqs,len(otus))
    #距離行列書き出し + Inter/Intra距離計算
    #f = open(os.path.join('./files', matrix_output))
    try:
        f = open(os.path.join(RESULT_FOLDER, matrix_output),"w")
        f.write(str(len(otus)))
        f.write("\n")
        for n in range(len(otus)):
            #f.write("%-30s " % otus[n][0:30])
            f.write(otus[n])
            f.write(" ")
            for m in range(len(otus)):
                score[m][n] = score[m][n] + 0.00000001 #minus zero
                f.write("%0.5f " % score[m][n])
            f.write("\r")
        f.close()
    except:
        raise Exception("Calculating Genetic Difference Error")
    #print(score)
    #print(otus)
    return (score, otus)

def phylo_tree(score, otus, tree, path=RESULT_FOLDER, out_tree='out_tree.txt'):
    #系統樹作成
    print("Create Phylogenetic Tree...")
    try:
        if tree == "nj":
            print("nj")
            Phylo.write(makeNj(score,otus), os.path.join(path, out_tree), "newick")
        elif tree == "upgma":
            print("upgma")
            Phylo.write(makeUpgma(score,otus), os.path.join(path, out_tree), "newick")
    except: 
        raise Exception("Phylogenetic Tree Generation Error")

def phylo_tree_score_otus(input_file, tree, path=RESULT_FOLDER, out_tree='out_tree.txt'):
    #系統樹作成
    score = []
    otus = []
    f = open(os.path.join(RESULT_FOLDER, input_file),"r")
    try:
        line_count = int(f.readline())
        for n in range(line_count):
            line = f.readline()
            line_read = line.split(" ",1)
            otus.append(line_read.pop(0))
            pre_score = line_read.pop(0)
            score.append(list(map(float, pre_score.split(" ")[:-1:])))
    except:
        raise Exception("No valid matrix") 
    f.close()
    print("Create Phylogenetic Tree...")
    try:
        if tree == "nj":
            print("nj")
            Phylo.write(makeNj(score,otus), os.path.join(path, out_tree), "newick")
        elif tree == "upgma":
            print("upgma")
            Phylo.write(makeUpgma(score,otus), os.path.join(path, out_tree), "newick")
    except: 
        raise Exception("Phylogenetic Tree Generation Error")

def parse_otus(input_file):

    otus = []
    seqs = []
    #ここでfiledateにファイル読み込む
    #try:
    #filedata = open(input_file,"r")
    filedata = open(os.path.join(RESULT_FOLDER, input_file),"r")
    for record in SeqIO.parse(filedata, "fasta"):
        #otu = str(record.id)
        otu = str(record.description)
        seq = str(record.seq).upper().replace("U","T")
        otus.append(otu)
        seqs.append(list(seq))
    filedata.close()
    return (otus, seqs)


def calcDiff_ami(model,plusgap,seqData,otu):
    score = [[0 for a in range(otu)] for b in range(otu)]

    if plusgap == "checked":
        lgs = len(seqData[0])

        if model == "JC":
            for a in range(otu):
                for b in range(a):
                    S = 0
                    D = 0
                    w = 1.0 - (seqData[a].count("-") + seqData[b].count("-"))/lgs*0.5
                    for i in range(lgs):
                        if seqData[a][i] == seqData[b][i]:
                            if seqData[a][i] != "-":
                                S += 1
                        else:
                             if (seqData[a][i] != "-") & (seqData[b][i] != "-"):
                                D += 1
                    try:
                        score[a][b] = 0 - 0.95 * w * math.log((S - D / 19) / lgs / w)
                    except:
                        raise Exception('log(0) in Distance Matrix Calculation. Check Type and Genetic Difference')
                    score[b][a] = score[a][b]
                    
        elif model == "P-distance":
            for a in range(otu):
                for b in range(a):
                    D = 0
                    for i in range(lgs):
                        if seqData[a][i] != seqData[b][i]:
                            D += 1
                            
                    score[a][b] = D / lgs
                    score[b][a] = score[a][b]

        
    elif plusgap == "not_checked":
        if model == "JC":
            for a in range(otu):
                for b in range(a):
                    S = 0
                    lgs = len(seqData[0])
                    for i in range(lgs):
                        if (seqData[a][i] == "-") | (seqData[b][i] == "-"):
                            lgs -= 1
                        elif seqData[a][i] == seqData[b][i]:
                            S += 1
                            
                    try:
                        #score[a][b] = 0 - math.log(S/lgs)
                        score[a][b] = 0 - 0.95 * math.log((20*S/lgs-1)/19)
                    except:
                        raise Exception('log(0) in Distance Matrix Calculation. Check Type and Genetic Difference')
                    score[b][a] = score[a][b]
        elif model == "P-distance":
            for a in range(otu):
                for b in range(a):
                    lgs = len(seqData[0])
                    D = 0
                    for i in range(lgs):
                        if (seqData[a][i] == "-") | (seqData[b][i] == "-"):
                            lgs -= 1
                        elif seqData[a][i] != seqData[b][i]:
                            D += 1
                            
                    score[a][b] = D / lgs
                    score[b][a] = score[a][b]
    
    return score



def calcDiff_ami_old(model,plusgap,seqData,otu):
#def calcDiffProtein(model,plusgap,seqData,otu):
    import math

    score = [[0 for a in range(otu)] for b in range(otu)]
    for a in range(otu):
        for b in range(a):
            X = 0
            G = 0
            S = 0
            D = 0
            try:
                for i in range(len(seqData[0])):
                    if seqData[a][i] == '-' and seqData[b][i] == '-':
                        X += 1
                    elif seqData[a][i] == '-' or seqData[b][i] == '-':
                        G += 1
                    elif seqData[a][i] == seqData[b][i]:
                        S += 1
                    else:
                        D += 1
            except IndexError:
                raise Exception('File is not aligned')

            ###変更箇所(1)ここから
            if plusgap == "not_checked":
                lgs = S + D
                S = S / lgs
                if model == "P-distance":
                    score[a][b] = 1 - S
                elif model == "PC":
                    try:
                        score[a][b] = 0 - math.log(S)
                    except:
                        raise Exception('log(0) in Distance Matrix Calculation. Check Type and Genetic Difference')
                elif model == "JC":
                    try:
                        score[a][b] = 0 - (19 / 20) * math.log((20 * S / 19) - 1 / 19)
                    except:
                        raise Exception('log(0) in Distance Matrix Calculation. Check Type and Genetic Difference')

            elif plusgap == "checked":
                lgs = X + G + S + D
                X = X / lgs
                G = G / lgs
                S = S / lgs
                w = 1 - (G/2 + X)

                if model == "P-distance":
                    score[a][b] = 1 - X - S
                elif model == "PC":
                    try:
                        score[a][b] = 0 - w * math.log(S/w)
                    except:
                        raise Exception('log(0) in Distance Matrix Calculation. Check Type and Genetic Difference')
                elif model == "JC":
                    try:
                        score[a][b] = 0 - (19 * w / 20) * math.log((S - D / 19) / w)
                    except:
                        raise Exception('log(0) in Distance Matrix Calculation. Check Type and Genetic Difference')
            ###変更箇所(2)ここまで

            score[b][a] = score[a][b]
    return score


###塩基配列の遺伝的差異行列生成
#input...進化モデル名、+Gapオプション、アライメント済配列、生物種数
#output...遺伝的差異行列
def calcDiff_nuc(model,plusgap,seqData,otu):
    # Example file: otu = 90, range(otu) = (0,90)
    # score: 90 x 90 Zero-Matrix
    # r = 5 x 5 Zero-Matrix
    score = [[0 for a in range(otu)] for b in range(otu)]
    lgs = len(seqData[0])
    
    if plusgap == "checked":
        if model == "K2P":
            for a in range(otu):
                for b in range(a):
                    P = 0
                    Q = 0
                    S = 0
                    w = 1.0 - (seqData[a].count("-") + seqData[b].count("-"))/lgs*0.5
                    for i in range(lgs):
                        seq_p = seqData[a][i] + seqData[b][i]
                        if seq_p in ["TT","CC","AA","GG"]:
                            S += 1
                        elif seq_p in ["TC","CT","AG","GA"]:
                            P += 1
                        elif seq_p in ["TA","AT","CG","GC","TG","GT","AC","CA"]:
                            Q += 1
                            
                    P = P / lgs
                    Q = Q / lgs
                    S = S / lgs
                    try:
                        score[a][b] = 0.75 * w * math.log(w) - 0.5 * w * math.log((S-P) * math.sqrt(S+P-Q))
                    except:
                        raise Exception('log(0) in Distance Matrix Calculation. Check Type and Genetic Difference')
                    score[b][a] = score[a][b]
                    
        elif model == "P-distance":
            for a in range(otu):
                for b in range(a):
                    D = 0
                    for i in range(lgs):
                        if seqData[a][i] != seqData[b][i]:
                            D += 1
                            
                    score[a][b] = D / lgs
                    score[b][a] = score[a][b]

        
    elif plusgap == "not_checked":
        if model == "K2P":
            for a in range(otu):
                for b in range(a):
                    P = 0
                    Q = 0
                    S = 0
                    for i in range(lgs):
                        seq_p = seqData[a][i] + seqData[b][i]
                        if seq_p in ["TT","CC","AA","GG"]:
                            S += 1
                        elif seq_p in ["TC","CT","AG","GA"]:
                            P += 1
                        elif seq_p in ["TA","AT","CG","GC","TG","GT","AC","CA"]:
                            Q += 1
                            
                    lgs_tmp = P + Q + S
                    P = P / lgs_tmp
                    Q = Q / lgs_tmp
                    try:
                        score[a][b] = 0 - math.log(1 - 2 * P - Q) * 0.5 - math.log(1 - 2 * Q) * 0.25
                    except:
                        raise Exception('log(0) in Distance Matrix Calculation. Check Type and Genetic Difference')
                    score[b][a] = score[a][b]
        elif model == "P-distance":
            for a in range(otu):
                for b in range(a):
                    S = 0
                    D = 0
                    for i in range(lgs):
                        seq_p = seqData[a][i] + seqData[b][i]
                        if seq_p in ["TT","CC","AA","GG"]:
                            S += 1
                        elif seq_p in ["TC","CT","AG","GA","TA","AT","CG","GC","TG","GT","AC","CA"]:
                            D += 1
                            
                    score[a][b] = D / (S+D)
                    score[b][a] = score[a][b]
    
    return score


###塩基配列の遺伝的差異行列生成
#input...進化モデル名、+Gapオプション、アライメント済配列、生物種数
#output...遺伝的差異行列
def calcDiff_nuc_old(model,plusgap,seqData,otu):   
#def calcDiff(model,plusgap,seqData,otu):   
    # Example file: otu = 90, range(otu) = (0,90)
    # score: 90 x 90 Zero-Matrix
    # r = 5 x 5 Zero-Matrix
    score = [[0 for a in range(otu)] for b in range(otu)]
    for a in range(otu):
        for b in range(a):
            r = [[0 for a in range(5)] for b in range(5)] # 0=A 1=T 2=G 3=C
            try:
                for i in range(len(seqData[0])):
                    if seqData[a][i] == '-' and seqData[b][i] == 'A':
                        r[0][1]+=1
                    elif seqData[a][i] == '-' and seqData[b][i] == 'T':
                        r[0][2]+=1
                    elif seqData[a][i] == '-' and seqData[b][i] == 'G':
                        r[0][3]+=1
                    elif seqData[a][i] == '-' and seqData[b][i] == 'C':
                        r[0][4]+=1
                    elif seqData[a][i] == 'A' and seqData[b][i] == '-':
                        r[1][0]+=1
                    elif seqData[a][i] == 'A' and seqData[b][i] == 'A':
                        r[1][1]+=1
                    elif seqData[a][i] == 'A' and seqData[b][i] == 'T':
                        r[1][2]+=1
                    elif seqData[a][i] == 'A' and seqData[b][i] == 'G':
                        r[1][3]+=1
                    elif seqData[a][i] == 'A' and seqData[b][i] == 'C':
                        r[1][4]+=1
                    elif seqData[a][i] == 'T' and seqData[b][i] == '-':
                        r[2][0]+=1
                    elif seqData[a][i] == 'T' and seqData[b][i] == 'A':
                        r[2][1]+=1
                    elif seqData[a][i] == 'T' and seqData[b][i] == 'T':
                        r[2][2]+=1
                    elif seqData[a][i] == 'T' and seqData[b][i] == 'G':
                        r[2][3]+=1
                    elif seqData[a][i] == 'T' and seqData[b][i] == 'C':
                        r[2][4]+=1
                    elif seqData[a][i] == 'G' and seqData[b][i] == '-':
                        r[3][0]+=1
                    elif seqData[a][i] == 'G' and seqData[b][i] == 'A':
                        r[3][1]+=1
                    elif seqData[a][i] == 'G' and seqData[b][i] == 'T':
                        r[3][2]+=1
                    elif seqData[a][i] == 'G' and seqData[b][i] == 'G':
                        r[3][3]+=1
                    elif seqData[a][i] == 'G' and seqData[b][i] == 'C':
                        r[3][4]+=1
                    elif seqData[a][i] == 'C' and seqData[b][i] == '-':
                        r[4][0]+=1
                    elif seqData[a][i] == 'C' and seqData[b][i] == 'A':
                        r[4][1]+=1
                    elif seqData[a][i] == 'C' and seqData[b][i] == 'T':
                        r[4][2]+=1
                    elif seqData[a][i] == 'C' and seqData[b][i] == 'G':
                        r[4][3]+=1
                    elif seqData[a][i] == 'C' and seqData[b][i] == 'C':
                        r[4][4]+=1
                    elif seqData[a][i] == '-' and seqData[b][i] == '-':
                        r[0][0]+=1
            except:
                raise Exception('File is not aligned')

            ###変更箇所(2)ここから
            if plusgap == "not_checked":
                lgs = r[1][1] + r[1][2] + r[1][3] + r[1][4] + r[2][1] + r[2][2] + r[2][3] + r[2][4] + r[3][1] + r[3][2] + r[3][3] + r[3][4] + r[4][1] + r[4][2] + r[4][3] + r[4][4]
                S = (r[1][1]+r[2][2]+r[3][3]+r[4][4])/lgs

                if model == "P-distance":
                    score[a][b] = 1 - S

                elif model == "PC":
                    try:
                        score[a][b] = 0 - math.log(S)
                    except:
                        raise Exception('log(0) in Distance Matrix Calculation. Check Type and Genetic Difference')

                elif model == "JC":
                    try:
                        score[a][b] = 0 - (3 / 4) * math.log((4 * S / 3) - 1 / 3)
                    except:
                        raise Exception('log(0) in Distance Matrix Calculation. Check Type and Genetic Difference')

                elif model == "K2P":
                    P = (r[1][3] + r[3][1] + r[2][4] + r[4][2]) / lgs
                    Q = (r[1][2] + r[2][1] + r[1][4] + r[4][1] + r[2][3] + r[3][2] + r[3][4] + r[4][3]) / lgs
                    try:
                        score[a][b] = 0 - math.log(1 - 2 * P - Q) / 2 - math.log(1 - 2 * Q) / 4
                    except:
                        raise Exception('log(0) in Distance Matrix Calculation. Check Type and Genetic Difference')

            elif plusgap == "checked":
                lgs = sum(r[0])+sum(r[1])+sum(r[2])+sum(r[3])+sum(r[4])

                S = (r[1][1]+r[2][2]+r[3][3]+r[4][4])/lgs
                G = (r[0][1]+r[0][2]+r[0][3]+r[0][4]+r[1][0]+r[2][0]+r[3][0]+r[4][0])/lgs
                X = r[0][0]/lgs
                w = 1 - (G/2 + X)

                if model == "P-distance":
                    score[a][b] = 1 - S - X

                elif model == "PC":
                    try:
                        score[a][b] = 0 - w * math.log(S/w)
                    except:
                        raise Exception('log(0) in Distance Matrix Calculation. Check Type and Genetic Difference')

                elif model == "JC":
                    D = 1 - S - G - X
                    try:
                        score[a][b] = 0 - (3 * w / 4) * math.log((S - D / 3) / w)
                    except:
                        raise Exception('log(0) in Distance Matrix Calculation. Check Type and Genetic Difference')

                elif model == "K2P":
                    P = (r[1][3]+r[3][1]+r[2][4]+r[4][2])/lgs
                    Q = (r[1][2]+r[2][1]+r[1][4]+r[4][1]+r[2][3]+r[3][2]+r[3][4]+r[4][3])/lgs
                    try:
                        score[a][b] = 0.75 * w * math.log(w) - 0.5 * w * math.log((S-P) * math.sqrt(S+P-Q))
                    except:
                        raise Exception('log(0) in Distance Matrix Calculation. Check Type and Genetic Difference')
                ###変更箇所(2)ここまで

            score[b][a] = score[a][b]
    return score

###NJ法による系統樹作成
#input...遺伝的差異行列
#output...Newick形式の系統樹
def makeNj(score,otuName):
    for i in range(len(score)):
        for j in range(len(score)):
            score[i][j] = round(score[i][j],6)
    clades = [BaseTree.Clade(None, name) for name in otuName]

    # init node distance
    node_dist = [0] * len(score)
    # init minimum index
    min_i = 0
    min_j = 0
    inner_count = 0
    while len(score) > 2:
        # calculate nodeDist
        for i in range(0, len(score)):
            node_dist[i] = 0
            for j in range(0, len(score)):
                node_dist[i] += score[i][j]
            node_dist[i] = node_dist[i] / (len(score) - 2)

        # find minimum distance pair
        min_dist = score[1][0] - node_dist[1] - node_dist[0]
        min_i = 0
        min_j = 1
        for i in range(1, len(score)):
            for j in range(0, i):
                temp = score[i][j] - node_dist[i] - node_dist[j]
                if min_dist > temp:
                    min_dist = temp
                    min_i = i
                    min_j = j
        # create clade
        clade1 = clades[min_i]
        clade2 = clades[min_j]
        inner_count += 1
        inner_clade = BaseTree.Clade(None, "Inner" + str(inner_count))
        inner_clade.clades.append(clade1)
        inner_clade.clades.append(clade2)
        # assign branch length
        clade1.branch_length = (score[min_i][min_j] + node_dist[min_i] - node_dist[min_j]) / 2.0
        clade2.branch_length = score[min_i][min_j] - clade1.branch_length

        # update node list
        clades[min_j] = inner_clade
        del clades[min_i]

        # rebuild distance matrix,
        # set the distances of new node at the index of min_j
        for k in range(0, len(score)):
            if k != min_i and k != min_j:
                score[min_j][k] = (score[min_i][k] + score[min_j][k] - score[min_i][min_j]) / 2.0
                score[k][min_j] = score[min_j][k]

        otuName[min_j] = "Inner" + str(inner_count)
        del score[min_i]
        for i in range(len(score)):
            del score[i][min_i]

    # set the last clade as one of the child of the inner_clade
    root = None
    if clades[0] == inner_clade:
        clades[0].branch_length = 0
        clades[1].branch_length = score[1][0]
        clades[0].clades.append(clades[1])
        root = clades[0]
    else:
        clades[0].branch_length = score[1][0]
        clades[1].branch_length = 0
        clades[1].clades.append(clades[0])
        root = clades[1]

    return BaseTree.Tree(root, rooted=False)

###UPMGA法による系統樹作成
#input...遺伝的差異行列
#output...Newick形式の系統樹

def height_of(clade):
        """Calculate clade height -- the longest path to any terminal (PRIVATE)."""
        height = 0
        if clade.is_terminal():
            height = clade.branch_length
        else:
            height = height + max(height_of(c) for c in clade.clades)
        return height

def makeUpgma(score,otuName):

    for i in range(len(score)):
        for j in range(len(score)):
            score[i][j] = round(score[i][j],6)

    clades = [BaseTree.Clade(None, name) for name in otuName]

    # init minimum index
    min_i = 0
    min_j = 0
    inner_count = 0
    while len(score) > 1:
        min_dist = score[1][0]
        # find minimum index
        for i in range(1, len(score)):
            for j in range(0, i):
                if min_dist >= score[i][j]:
                    min_dist = score[i][j]
                    min_i = i
                    min_j = j

        # create clade
        clade1 = clades[min_i]
        clade2 = clades[min_j]
        inner_count += 1
        inner_clade = BaseTree.Clade(None, "Inner" + str(inner_count))
        inner_clade.clades.append(clade1)
        inner_clade.clades.append(clade2)
        # assign branch length

        # TODO: originally self._height_of function from github repo 
        #       was called but not implemented in this code. 
        #       Function was input above.
        if clade1.is_terminal():
            clade1.branch_length = min_dist * 1.0 / 2
        else:
            clade1.branch_length = min_dist * \
                1.0 / 2 - height_of(clade1)

        if clade2.is_terminal():
            clade2.branch_length = min_dist * 1.0 / 2
        else:
            clade2.branch_length = min_dist * \
                1.0 / 2 - height_of(clade2)
        ################################################################
        ################################################################
        ################################################################
        # update node list
        clades[min_j] = inner_clade
        del clades[min_i]

        # rebuild distance matrix,
        # set the distances of new node at the index of min_j
        for k in range(0, len(score)):
            if k != min_i and k != min_j:
                score[min_j][k] = (score[min_i][k] + score[min_j][k]) * 1.0 / 2
                score[k][min_j] = score[min_j][k]

        otuName[min_j] = "Inner" + str(inner_count)
        del score[min_i]
        for i in range(len(score)):
            del score[i][min_i]

    inner_clade.branch_length = 0
    return BaseTree.Tree(inner_clade)

if __name__ == '__main__':
    results = main(docopt(__doc__))
    if results[0] == "Complete.":
        DL_message = "[DOWNLOAD]"
        DL_alignment = "alignment.txt"
        DL_matrix = "matrix.txt"
        DL_tree = "tree.txt"
        DL_alignment_result = results[1]
        DL_matrix_result = results[2]
        DL_tree_result = results[3]

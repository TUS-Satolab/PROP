"""
calculation

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
"""

import datetime, time, subprocess, shutil, sys, os, Bio, math
from docopt import docopt
from flask import Flask, render_template, request
from Bio import Phylo, SeqIO
from Bio.Phylo import BaseTree

def calculation(args):
    #タイムスタンプ取得(ファイル名に使うのみ)
    start = time.time()
    timestamp = datetime.datetime.today().strftime("%Y-%m-%d-%H-%M-%S")
    out_align = timestamp + "align.txt"
    out_matrix = timestamp + "matrix.txt"
    out_tree = timestamp + "tree.txt"
    current_dir = os.getcwd()
    ############ docopt arguments ###############
    filename = args["--filename"]
    data_type = args["--type"]
    align = args["--align"]
    align_clw_opt = args["--align_clw_opt"]
    
    model = args["--model"]
    plusgap = args["--plusgap"]
    gapdel = args["--gapdel"]
    tree = args["--tree"]
    #アライメント
    if align_clw_opt == "(default)":
        align_clw_opt = ""

    # TODO: Make this prettier
    if align == "none":
        #ファイルコピー
        shutil.copy(filename, out_align)
    elif data_type == "nuc" and align == "clustalw":
        subprocess.call("docker run -v "+ current_dir +":/data --rm my_clustalw clustalw \
                -INFILE=" + filename + " -OUTFILE=./" + out_align + \
                " -OUTPUT=PIR -OUTORDER=INPUT -TYPE=DNA "+align_clw_opt,shell=True)
    elif data_type == "ami" and align == "clustalw":
        # TODO: originally out_align/Align.txt name but I don't see the reason why
        subprocess.call("docker run -v "+ current_dir +":/data --rm my_clustalw clustalw \
                -INFILE=" + filename + " -OUTFILE=./" + out_align + \
                 " -OUTPUT=PIR -OUTORDER=INPUT -TYPE=PROTEIN "+align_clw_opt,shell=True)
    # TODO: Make sure what outputs are necessary for it
    elif data_type in ["nuc", "ami"] and align == "mafft":
        subprocess.call("docker run -v "+ current_dir +":/data --rm my_mafft mafft "+ filename +" > "+ out_align,shell=True)
    else:
        raise Exception("Check datatype or align definitions")

    # TODO: is it correct to input the aligned file? Get error otherwise
    (otus, seqs) = parse_otus(out_align) 

    #Complete Deletionオプション(plusGapオプションなしの場合)
    if plusgap == "":
        if gapdel == "comp":
            for i in range(len(seqs[0])):
                for j in range(len(otus)):
                    if seqs[j][i] == "-":
                        for k in range(len(otus)):
                            tmp = list(seqs[k])
                            tmp[i] = "-"
                            seqs[k] = "".join(tmp)

    #距離行列作成
    print("Create Distance Matrix...")
    try:
        if data_type == "nuc":
            score = calcDiff(model,plusgap,seqs,len(otus))
        elif data_type == "ami":
            score = calcDiffProtein(model,plusgap,seqs,len(otus))
        #距離行列書き出し + Inter/Intra距離計算
        f = open(out_matrix,"w")
        f.write("%s\n" % str(len(otus)))
        for n in range(len(otus)):
            f.write("%-30s " % otus[n][0:30])
            for m in range(len(otus)):
                score[m][n] = score[m][n] + 0.00000000001 #マイナスゼロ対策
                f.write("%0.5f " % score[m][n])
            f.write("\r")
        f.close()
    except:
        raise Exception("遺伝的差異計算Error",0,0,0)

    

    #系統樹作成
    print("Create Phylogenetic Tree...")
    try:
        if tree == "nj":
            Phylo.write(makeNj(score,otus), out_tree, "newick")
        elif tree == "upgma":
            Phylo.write(makeUpgma(score,otus), out_tree, "newick")
    except: 
        raise Exception("系統樹作成Error",0,0,0)

    #ここまで行ったら結果出力する
    #結果表示
    f = open(out_align)
    align_result = f.read()
    f.close()
    f = open(out_matrix)
    matrix_result = f.read()
    f.close()
    f = open(out_tree)
    tree_result = f.read()
    f.close()
    #os.remove(out_align)
    #os.remove(out_matrix)
    #os.remove(out_tree)

    return ["Complete.",align_result.replace("\n","NEWLINE"),matrix_result.replace("\n","NEWLINE"),tree_result.replace("\n","NEWLINE")]
def parse_otus(filename):

    otus = []
    seqs = []
    #ここでfiledateにファイル読み込む
    #try:
    filedata = open(filename,"r")
    for record in SeqIO.parse(filedata, "fasta"):
        otu = str(record.id)
        seq = str(record.seq).upper().replace("U","T")
        otus.append(otu)
        seqs.append(list(seq))
    filedata.close()
    return (otus, seqs)

def calcDiffProtein(model,plusgap,seqData,otu):
    import math

    score = [[0 for a in range(otu)] for b in range(otu)]
    for a in range(otu):
        for b in range(a):
            X = 0
            G = 0
            S = 0
            D = 0
            for i in range(len(seqData[0])):
                if seqData[a][i] == '-' and seqData[b][i] == '-':
                    X += 1
                elif seqData[a][i] == '-' or seqData[b][i] == '-':
                    G += 1
                elif seqData[a][i] == seqData[b][i]:
                    S += 1
                else:
                    D += 1

            ###変更箇所(1)ここから
            if plusgap == "":
                lgs = S + D
                S = S / lgs
                if model == "P":
                    score[a][b] = 1 - S
                elif model == "PC":
                    score[a][b] = 0 - math.log(S)
                elif model == "JC":
                    score[a][b] = 0 - (19 / 20) * math.log((20 * S / 19) - 1 / 19)

            elif plusgap == "checked":
                lgs = X + G + S + D
                X = X / lgs
                G = G / lgs
                S = S / lgs
                w = 1 - (G/2 + X)

                if model == "P":
                    score[a][b] = 1 - X - S
                elif model == "PC":
                    score[a][b] = 0 - w * math.log(S/w)
                elif model == "JC":
                    score[a][b] = 0 - (19 * w / 20) * math.log((S - D / 19) / w)
            ###変更箇所(2)ここまで

            score[b][a] = score[a][b]
    return score

###塩基配列の遺伝的差異行列生成
#input...進化モデル名、+Gapオプション、アライメント済配列、生物種数
#output...遺伝的差異行列
def calcDiff(model,plusgap,seqData,otu):   
    # Example file: otu = 90, range(otu) = (0,90)
    # score: 90 x 90 Zero-Matrix
    # r = 5 x 5 Zero-Matrix
    score = [[0 for a in range(otu)] for b in range(otu)]
    for a in range(otu):
        for b in range(a):
            r = [[0 for a in range(5)] for b in range(5)] # 0=A 1=T 2=G 3=C
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

            ###変更箇所(2)ここから
            if plusgap == "":
                lgs = r[1][1] + r[1][2] + r[1][3] + r[1][4] + r[2][1] + r[2][2] + r[2][3] + r[2][4] + r[3][1] + r[3][2] + r[3][3] + r[3][4] + r[4][1] + r[4][2] + r[4][3] + r[4][4]
                S = (r[1][1]+r[2][2]+r[3][3]+r[4][4])/lgs

                if model == "P":
                    score[a][b] = 1 - S

                elif model == "PC":
                    score[a][b] = 0 - math.log(S)

                elif model == "JC":
                    score[a][b] = 0 - (3 / 4) * math.log((4 * S / 3) - 1 / 3)

                elif model == "K2P":
                    P = (r[1][3] + r[3][1] + r[2][4] + r[4][2]) / lgs
                    Q = (r[1][2] + r[2][1] + r[1][4] + r[4][1] + r[2][3] + r[3][2] + r[3][4] + r[4][3]) / lgs
                    score[a][b] = 0 - math.log(1 - 2 * P - Q) / 2 - math.log(1 - 2 * Q) / 4

            elif plusgap == "checked":
                lgs = sum(r[0])+sum(r[1])+sum(r[2])+sum(r[3])+sum(r[4])

                S = (r[1][1]+r[2][2]+r[3][3]+r[4][4])/lgs
                G = (r[0][1]+r[0][2]+r[0][3]+r[0][4]+r[1][0]+r[2][0]+r[3][0]+r[4][0])/lgs
                X = r[0][0]/lgs
                w = 1 - (G/2 + X)

                if model == "P":
                    score[a][b] = 1 - S - X

                elif model == "PC":
                    score[a][b] = 0 - w * math.log(S/w)

                elif model == "JC":
                    D = 1 - S - G - X
                    score[a][b] = 0 - (3 * w / 4) * math.log((S - D / 3) / w)

                elif model == "K2P":
                    P = (r[1][3]+r[3][1]+r[2][4]+r[4][2])/lgs
                    Q = (r[1][2]+r[2][1]+r[1][4]+r[4][1]+r[2][3]+r[3][2]+r[3][4]+r[4][3])/lgs
                    score[a][b] = 0.75 * w * math.log(w) - 0.5 * w * math.log((S-P) * math.sqrt(S+P-Q))
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
    results = calculation(docopt(__doc__))
    if results[0] == "Complete.":
        DL_message = "[DOWNLOAD]"
        DL_alignment = "alignment.txt"
        DL_matrix = "matrix.txt"
        DL_tree = "tree.txt"
        DL_alignment_result = results[1]
        DL_matrix_result = results[2]
        DL_tree_result = results[3]

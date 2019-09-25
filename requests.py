from flask import Flask, request, flash, redirect, url_for, send_from_directory, jsonify
from calculation import alignment, distance_matrix, phylo_tree
from werkzeug.utils import secure_filename
from zipfile import ZipFile
import datetime, time, os, uuid, pickle, glob

# Global variables
UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "/files"
ZIPPED_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "/zipped"
ALLOWED_EXTENSIONS = {'fasta', 'txt'}
flag = 0

app = Flask(__name__)
app.secret_key = "Nj#z2L86|!'=Cw&CG"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def zipFilesInDir(dirName, zipFileName, filter):
   # create a ZipFile object
   with ZipFile(zipFileName, 'w') as zipObj:
       # Iterate over all the files in directory
       for filename in os.listdir(dirName):
           if filter(filename):
               print(filename)
               # Add file to zip
               zipObj.write(os.path.join(dirName, filename), "./"+filename)

@app.route('/')
def index():
    return('Blank Page. To be filled.')

# Helper function for allowed files
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# File Upload
# necessary input: 
# file: [select file]
@app.route('/upload', methods=['GET', 'POST'])
def upload_file(f_name):
    f_name = f_name
    if request.method == 'POST':
        file = request.files[str(f_name)]

        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            #return redirect(request.url)
            return None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            task_id = str(uuid.uuid4())
            filename_with_id = "{0}_{2}.{1}".format(*filename.rsplit('.', 1) + [task_id])
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename_with_id))
            return (filename_with_id, task_id)
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

# necessary input: 
# file: [select file]
# MIND THE CORRECT NAMING
# align_method: clustalw or mafft
# input_type: nuc or ami [not necessary for mafft]
@app.route('/alignment', methods=['GET', 'POST'])
def align(flag=0):
    if request.method == 'POST':
        (filename, task_id) = upload_file('file')
        if not filename.endswith('.fasta'):
            flash('File format not correct. Choose fasta file')
            return redirect(request.url)
        align_method = request.form['align_method']
        input_type = request.form['input_type']
        align_clw_opt = request.form['align_clw_opt']
        out_align = "align_"+ task_id +".txt"
        print(out_align)
        alignment(out_align, filename, input_type, align_method, align_clw_opt)
        print("flag in align is", flag)
        if flag == 0:
            result = {
                "jobID": task_id,
                "input filename": filename,
                "output filename": out_align
            }
            return jsonify(result)
        else:
            print("I am here at align")
            return task_id
    else:
        return 'Use POST'

@app.route('/get_result', methods=['GET', 'POST'])
def uploaded_file(result_id=None, flag=0):
    if request.method == 'POST':
        if flag == 0:
            result_id = request.form['result_id']
        result_zip = 'results_' + result_id + '.zip'
        zipFilesInDir(UPLOAD_FOLDER, ZIPPED_FOLDER+"/"+result_zip, lambda name : result_id in name)

        #upload_file = "align_"+result_id+".txt"
        #print(upload_file)
        if os.path.exists(ZIPPED_FOLDER+"/"+result_zip):
            return send_from_directory(app.config['ZIPPED_FOLDER'], result_zip)
        else:
            return redirect(request.url)

# necessary input: 
# file: or task ID
# task_id: from previous step
# plusgap: "checked" / ""
# gapdel: "comp" / "pair"
# TODO: For the HTML dropdown list input: "comp" / "pair"
# input_type: nuc or ami [not necessary for mafft]
# model: P, PC, JS or K2P
@app.route('/matrix', methods=['GET', 'POST'])
def matrix(task_id=None, flag=0):
    if request.method == 'POST':
        # get inputs from alignment call: out_align
        # either input the task ID if out_align was created in the previous step or upload out_align manually
        # create matrix_output name with either task ID from previous step or give it new task ID
        if flag == 0:
            try:
                file = request.files['file']
            except:
                file = None
            task_id = request.form['task_id'] or None
        else:
            file = None
        if task_id is not None and file is None:
            filename = "align_" + task_id + ".txt"
        elif task_id is None and file is not None:
            (filename, task_id) = upload_file('file')
        elif task_id is not None and file is not None:
            flash('Choose either task ID or upload a file, not both')
            return redirect(request.url)
        # TODO: Handle the case that user inputs wrong task ID
        else:
            flash('Choose task ID or upload a file to proceed')
            return redirect(request.url)

        matrix_output = "matrix_"+task_id+".txt"
        if request.form.get("plusgap"):
            plusgap_checked = "checked"
        gapdel = request.form.get("gapdel", None)
        input_type = request.form['input_type']
        model = request.form['model']
        (score, otus) = distance_matrix(filename, matrix_output, gapdel, input_type, model, plusgap_checked)

        score_with_id = "score_" + task_id
        otus_with_id = "otus_" + task_id
        if flag == 0:
            # Pickle is used to preserve structure of list and dict
            with open(UPLOAD_FOLDER+"/"+score_with_id, 'wb') as score_p_file:
                pickle.dump(score, score_p_file)

            with open(UPLOAD_FOLDER+"/"+otus_with_id, 'wb') as otus_p_file:
                pickle.dump(otus, otus_p_file)

            result = {
                "jobID": task_id,
                "input filename": filename,
                "output filename": matrix_output
            }
            return jsonify(result)
        else:
            return (score, otus)

# necessary input: 
# score: [file name]
# otus: [file name]
# task_id: [if files are not specified]
# tree: nj or upgma
@app.route('/tree', methods=['GET', 'POST'])
def tree(score=None, otus=None, task_id=None, flag=0):
    if request.method == 'POST':
        if flag == 0:
            # Upload scores and otus OR input job ID
            try:
                file_score = request.files['score']
                file_otus = request.files['otus']
            except:
                file_score = None
                file_otus = None
            task_id = request.form['task_id'] or None
        else:
            file_score = None
            file_otus = None

        if task_id is not None:
            if file_score is None and file_otus is None:
                score_with_id = "score_" + task_id
                otus_with_id = "otus_" + task_id
            else:
                flash("Either define a task ID or upload score and otus.")
        elif task_id is None:
            if file_score is not None and file_otus is not None:
                # Upload of score and otus
                # changing of otus task id to score task id to have corresponding task ids
                (score_with_id, task_id) = upload_file('score')
                (otus_with_id, task_id_otus) = upload_file('otus')
                path_otus = os.path.join(UPLOAD_FOLDER,otus_with_id)
                newname_otus = path_otus.replace(task_id_otus, task_id)
                os.rename(path_otus,newname_otus)
                otus_with_id = os.path.basename(newname_otus)
            else:
                flash("Upload score and otus file")
                return redirect(request.url)
        else:
            flash('Choose task ID or upload score and otus file to proceed')
            return redirect(request.url)
        # TODO: Handle the case that user inputs wrong task ID
        
        if flag == 0:
            # Pickle is used to preserve structure of list and dict
            with open(UPLOAD_FOLDER+"/"+score_with_id, 'rb') as score_p_file:
                score = pickle.load(score_p_file)
            with open(UPLOAD_FOLDER+"/"+otus_with_id, 'rb') as otus_p_file:
                otus = pickle.load(otus_p_file)

        tree = request.form['tree']
        out_tree = "tree_"+task_id+".txt"
        phylo_tree(score, otus, tree, UPLOAD_FOLDER, out_tree)
        if flag == 0:
            result = {
                "jobID": task_id,
                "input filename score": score_with_id,
                "input filename otus": otus_with_id,
                "output filename": out_tree
            }
            return jsonify(result)
        else:
            return 'Finished'

# necessary input: 
# file: [select file]
# MIND THE CORRECT NAMING
# align_method: clustalw or mafft
# input_type: nuc or ami [not necessary for mafft]
# file: or task ID
# task_id: from previous step
# plusgap: "checked" / ""
# gapdel: "comp" / "pair"
# TODO: For the HTML dropdown list input: "comp" / "pair"
# model: P, PC, JS or K2P
# score: [file name]
# otus: [file name]
# task_id: [if files are not specified]
# tree: nj or upgma
@app.route('/complete', methods=['GET', 'POST'])
def complete():
    # signal for directly computing everything
    flag = 1

    task_id = align(flag)
    (score, otus) = matrix(task_id, flag)
    tree(score, otus, task_id, flag)

    # output the three files align, matrix and tree
    #uploaded_file(task_id, flag)
    return task_id
    flag = 0
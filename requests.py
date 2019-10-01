from flask import Flask, request, flash, redirect, url_for, send_from_directory, jsonify, render_template
from calculation import alignment, distance_matrix, phylo_tree, complete_calc
from werkzeug.utils import secure_filename
from zipfile import ZipFile
from redis import Redis
from rq import Queue
from rq.job import Job
import datetime, time, os, uuid, pickle, glob



# Global variables
UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "/files"
ZIPPED_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "/zipped"
ALLOWED_EXTENSIONS = {'fasta', 'txt', 'fa'}

app = Flask(__name__)
app.secret_key = "Nj#z2L86|!'=Cw&CG"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ZIPPED_FOLDER'] = ZIPPED_FOLDER


def zipFilesInDir(dirName, zipFileName, filter):
   # create a ZipFile object
   with ZipFile(zipFileName, 'w') as zipObj:
       # Iterate over all the files in directory
       for filename in os.listdir(dirName):
           if filter(filename):
               print(filename)
               # Add file to zip
               zipObj.write(os.path.join(dirName, filename), "./"+filename)

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
def align(task_id=None, filename=None):
    if request.method == 'POST':
        if request.form['submit_button'] == 'go_back':
                return redirect(url_for('index'))
        elif request.form['submit_button'] == 'calculate':
            (filename, task_id) = upload_file('file')
            if not filename.endswith('.fasta'):
                flash('File format not correct. Choose fasta file')
                return redirect(request.url)
            align_method = request.form['align_method']
            input_type = request.form['input_type']
            align_clw_opt = request.form['align_clw_opt']
            out_align = "align_"+ task_id +".txt"

            q = Queue(connection=Redis('localhost', 6379))
            #job = q.enqueue(complete_calc,job_id=task_id, task_id=task_id,filename=filename)
            job = q.enqueue(alignment,
                            job_id=task_id,
                            ###############################
                            ###############################
                            job_timeout='30m', # TODO set it back to 30m
                            ###############################
                            ###############################
                            args=(out_align, filename, input_type, 
                                align_method, align_clw_opt))
            return render_template('get_completed_results_form.html', msg=task_id)
            #return render_template('get_result_form.html', msg=task_id)
    else:
        return render_template('alignment_form.html')

@app.route('/get_result', methods=['GET', 'POST'])
def get_result(result_id=None):
    if request.method == 'POST':
        if request.form['submit_button'] == 'go_back':
                return redirect(url_for('index'))
        elif request.form['submit_button'] == 'get_result':
            result_id = request.form['result_id']
            result_zip = 'results_' + result_id + '.zip'
            zipFilesInDir(UPLOAD_FOLDER, ZIPPED_FOLDER+"/"+result_zip, lambda name : result_id in name)

            #upload_file = "align_"+result_id+".txt"
            #print(upload_file)
            if os.path.exists(ZIPPED_FOLDER+"/"+result_zip):
                return send_from_directory(app.config['ZIPPED_FOLDER'], result_zip)
            else:
                return redirect(request.url)
    else:
        return render_template('get_result_form.html')

@app.route('/get_result_completed', methods=['GET', 'POST'])
def get_result_completed(result_id=None):
    if request.method == 'POST':
        if request.form['submit_button'] == 'go_back':
                return redirect(url_for('index'))
        elif request.form['submit_button'] == 'get_result':
            result_id = request.form['result_id']
            redis = Redis()
            job = Job.fetch(result_id, connection=redis)
            print('Status: %s' % job.get_status())
            if job.get_status() == 'finished':
                result_zip = 'results_' + result_id + '.zip'
                zipFilesInDir(UPLOAD_FOLDER, ZIPPED_FOLDER+"/"+result_zip, lambda name : result_id in name)
                if os.path.exists(ZIPPED_FOLDER+"/"+result_zip):
                    return send_from_directory(app.config['ZIPPED_FOLDER'], result_zip)
                else:
                    flash("Something went wrong.")
                    return redirect(request.url)
            elif job.get_status() == 'queued':
                flash("The job is still in the queue")
                return redirect(request.url)
            elif job.get_status() == 'started':
                flash("The job is still running")
                return redirect(request.url)
            elif job.get_status() == 'failed':
                flash("The job failed. Either it took longer than 30 minutes or the provided file is not correct.")
                return redirect(request.url)
    else:
        return render_template('get_completed_results_form.html')

# necessary input: 
# file: or task ID
# task_id: from previous step
# plusgap: "checked" / ""
# gapdel: "comp" / "pair"
# TODO: For the HTML dropdown list input: "comp" / "pair"
# input_type: nuc or ami [not necessary for mafft]
# model: P, PC, JS or K2P
@app.route('/matrix', methods=['GET', 'POST'])
def matrix(task_id=None):
    if request.method == 'POST':
        # get inputs from alignment call: out_align
        # either input the task ID if out_align was created in the previous step or upload out_align manually
        # create matrix_output name with either task ID from previous step or give it new task ID
        if request.form['submit_button'] == 'go_back':
                return redirect(url_for('index'))
        elif request.form['submit_button'] == 'calculate':
            try:
                file = request.files['file']
                if file.filename == '':
                    file = None
            except:
                file = None
            task_id = request.form['task_id'] or None
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

            if request.form.get("plusgap"):
                plusgap_checked = "checked"
            else:
                plusgap_checked = None
            gapdel = request.form.get("gapdel", None)
            input_type = request.form['input_type']
            model = request.form['model']
            matrix_output = "matrix_"+task_id+".txt"

            q = Queue(connection=Redis('localhost', 6379))
            #job = q.enqueue(complete_calc,job_id=task_id, task_id=task_id,filename=filename)
            job = q.enqueue(distance_matrix,
                            job_id=task_id,
                            job_timeout='30m', 
                            args=(filename, matrix_output, gapdel, 
                                input_type, model, plusgap_checked))
            #score_with_id = "score_" + task_id
            #otus_with_id = "otus_" + task_id
            #(score, otus) = distance_matrix(filename, matrix_output, gapdel, input_type, model, plusgap_checked)            
            # Pickle is used to preserve structure of list and dict
            #with open(UPLOAD_FOLDER+"/"+score_with_id, 'wb') as score_p_file:
            #    pickle.dump(score, score_p_file)

            #with open(UPLOAD_FOLDER+"/"+otus_with_id, 'wb') as otus_p_file:
            #    pickle.dump(otus, otus_p_file)

            #return render_template('get_result_form.html', msg=task_id)
            return render_template('get_completed_results_form.html', msg=task_id)

    else:
        return render_template('distance_matrix_form.html')

# necessary input: 
# score: [file name]
# otus: [file name]
# task_id: [if files are not specified]
# tree: nj or upgma
@app.route('/tree', methods=['GET', 'POST'])
def tree(score=None, otus=None, task_id=None):
    if request.method == 'POST':
        if request.form['submit_button'] == 'go_back':
                return redirect(url_for('index'))
        elif request.form['submit_button'] == 'calculate':
            # Upload distance matrix file OR input job ID
            file = request.files['file']
            if file.filename == '':
                file = None
            task_id = request.form['task_id'] or None

            # Just upload Matrix file. Get rid of score and otus
            # get rid of score_with_id and otus_with_id
            # implement queueing system



            if task_id is not None:
                if file is None:
                    score_with_id = "score_" + task_id
                    otus_with_id = "otus_" + task_id
                else:
                    flash("Either define a task ID or upload score and otus.")
            elif task_id is None:
                ########## Conversion from Distance Matrix to score and otus variables
                if file is not None:
                    # Upload of distance matrix
                    # score and otus variables are calculated
                    (filename, task_id) = upload_file('file')
                    score = []
                    otus = []
                    f = open(os.path.join(app.config['UPLOAD_FOLDER'], filename), "r")
                    line_count = int(f.readline())
                    for n in range(line_count):
                        line = f.readline()
                        line_read = line.split(" ",1)
                        print("This happened at", n)
                        print(line_read)
                        otus.append(line_read.pop(0))
                        pre_score = line_read.pop(0)
                        print(pre_score)
                        score.append(list(map(float, pre_score.split(" ")[:-1:])))
                else:
                    flash("Upload Distance matrix file")
                    return redirect(request.url)
            else:
                flash('Choose task ID or upload distance matrix file to proceed')
                return redirect(request.url)
            # TODO: Handle the case that user inputs wrong task ID
            

            if file == None:
                # Pickle is used to preserve structure of list and dict
                with open(UPLOAD_FOLDER+"/"+score_with_id, 'rb') as score_p_file:
                    score = pickle.load(score_p_file)
                with open(UPLOAD_FOLDER+"/"+otus_with_id, 'rb') as otus_p_file:
                    otus = pickle.load(otus_p_file)
            tree = request.form['tree']
            out_tree = "tree_"+task_id+".txt"
            phylo_tree(score, otus, tree, UPLOAD_FOLDER, out_tree)
            return render_template('get_result_form.html', msg=task_id)
    else:
        return render_template('tree_form.html')

# necessary input: 
# file: [select file]
# MIND THE CORRECT NAMING
# align_method: clustalw or mafft
# input_type: nuc or ami [not necessary for mafft]
# align_clw_opt: [string]
# plusgap: "checked" / ""
# gapdel: "comp" / "pair"
# model: P, PC, JS or K2P
# tree: nj or upgma

#def complete_calc(task_id,filename,flag=1):
#    align(task_id=task_id, filename=filename, flag=1)
#    (score, otus) = matrix(task_id, flag=1)
#    tree(score, otus, task_id, flag=1)
#    return('This worked.')

@app.route('/complete', methods=['GET', 'POST'])
def complete():
    if request.method == 'POST':
        if request.form['submit_button'] == 'go_back':
                return redirect(url_for('index'))
        elif request.form['submit_button'] == 'calculate':
            (filename, task_id) = upload_file('file')
            if not filename.endswith(('.fasta', '.fa')):
                flash('File format not correct. Choose fasta file')
                return redirect(request.url)
            
            align_method = request.form['align_method']
            input_type = request.form['input_type']
            align_clw_opt = request.form['align_clw_opt']
            if request.form.get("plusgap"):
                plusgap_checked = "checked"
            gapdel = request.form.get("gapdel", None)
            model = request.form['model']
            tree = request.form['tree']

            out_align = "align_"+ task_id +".txt"
            matrix_output = "matrix_"+task_id+".txt"
            out_tree = "tree_"+task_id+".txt"

            q = Queue(connection=Redis('localhost', 6379))
            #job = q.enqueue(complete_calc,job_id=task_id, task_id=task_id,filename=filename)
            job = q.enqueue(complete_calc,
                            job_id=task_id,
                            ###############################
                            ###############################
                            job_timeout='1m', # TODO set it back to 30m
                            ###############################
                            ###############################
                            args=(out_align, filename, input_type, align_method, 
                                align_clw_opt, matrix_output, gapdel, model, 
                                tree, UPLOAD_FOLDER, out_tree, plusgap_checked))
            time.sleep(1)
            queued_job_ids = q.job_ids
            print(queued_job_ids)
            ################################################################
            ### This goes into the queue #########
            #align(task_id=task_id, filename=filename, flag=1)
            #(score, otus) = matrix(task_id, flag=1)
            #tree(score, otus, task_id, flag=1)
            ################################################################
            ### This goes into the queue #########
            
            # this should change to "Redirect user to a page where he gets the task id" comment
            #return render_template('get_result_form.html', msg=task_id)
            # Put tasks in queue
            # Redirect user to a page where he gets the task id
            # Add a message on the get_result page, how far the calculation has proceeded 
            return render_template('get_completed_results_form.html', msg=task_id)
            
            

            
    else:
        return render_template('complete_calc_form.html')


# Website Stuff
@app.route('/')
def index():
    return render_template('index.html')




if __name__ == "__main__":
    app.run(debug=True)
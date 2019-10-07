from flask import Flask, request, flash, redirect, url_for, send_from_directory, jsonify, render_template
from calculation import alignment, distance_matrix, phylo_tree, complete_calc
from werkzeug.utils import secure_filename
from zipfile import ZipFile
from redis import Redis
from rq import Queue, Connection, Worker, registry
from rq.job import Job
import datetime, time, os, uuid, pickle, glob, redis, rq_dashboard


# Global variables
UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "/files"
ZIPPED_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "/zipped"
ALLOWED_EXTENSIONS = {'fasta', 'txt', 'fa'}

app = Flask(__name__)
app.config.from_object(rq_dashboard.default_settings)
app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rq")
app.secret_key = "Nj#z2L86|!'=Cw&CG"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ZIPPED_FOLDER'] = ZIPPED_FOLDER
app.config['REDIS_URL'] = 'redis://redis:6379/0'
redis_url = app.config['REDIS_URL']
redis_connection = redis.from_url(redis_url)

def open_matrix(filename, otus, score):
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
    f.close()
    return (score, otus)

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

            q = Queue(connection=redis_connection)
            job = q.enqueue(alignment,
                            job_id=task_id,
                            job_timeout='30m',
                            result_ttl='168h',
                            args=(out_align, filename, input_type, align_method,  align_clw_opt))
            return render_template('get_completed_results_form.html', msg=task_id)
    else:
        return render_template('alignment_form.html')

@app.route('/get_result_completed', methods=['GET', 'POST'])
def get_result_completed(result_id=None):
    if request.method == 'POST':
        if request.form['submit_button'] == 'go_back':
                return redirect(url_for('index'))
        elif request.form['submit_button'] == 'get_result':
            result_id = request.form['result_id']
            try:
                job = Job.fetch(result_id, connection=redis_connection)
            except:
                flash("The job ID was not found. Make sure you have pasted the full ID")
                return redirect(request.url)
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
# input_type: nuc or ami [not necessary for mafft]
# model: P, PC, JS or K2P
@app.route('/matrix', methods=['GET', 'POST'])
def matrix(task_id=None):
    if request.method == 'POST':
        if request.form['submit_button'] == 'go_back':
                return redirect(url_for('index'))
        elif request.form['submit_button'] == 'calculate':
            file = request.files['file'] or None
            task_id = request.form['task_id'] or None
            if task_id is not None and file is None:
                filename = "align_" + task_id + ".txt"
                try:
                    f = open(os.path.join(app.config['UPLOAD_FOLDER'], filename), "r")
                    f.close()
                except:
                    flash("task ID was not found in the database. Make sure you pasted the complete ID.")
                    return redirect(request.url)
            elif task_id is None and file is not None:
                (filename, task_id) = upload_file('file')
            elif task_id is not None and file is not None:
                try:
                    filename = "align_" + task_id + ".txt"
                    f = open(os.path.join(app.config['UPLOAD_FOLDER'], filename), "r")
                    f.close()
                    flash("Task ID was used because Matrix File was found in the database")
                except:
                    (filename, task_id) = upload_file('file')
                    flash("File was uploaded because task ID was not found")
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

            q = Queue(connection=redis_connection)
            job = q.enqueue(distance_matrix,
                            job_id=task_id,
                            job_timeout='30m',
                            result_ttl='168h',
                            args=(filename, matrix_output, gapdel, 
                                input_type, model, plusgap_checked))
            return render_template('get_completed_results_form.html', msg=task_id)

    else:
        return render_template('distance_matrix_form.html')

# necessary input: 
# score: [file name]
# otus: [file name]
# task_id: [if files are not specified]
# tree: nj or upgma
@app.route('/tree', methods=['GET', 'POST'])
def tree():
    if request.method == 'POST':
        if request.form['submit_button'] == 'go_back':
                return redirect(url_for('index'))
        elif request.form['submit_button'] == 'calculate':
            file = request.files['file'] or None
            task_id = request.form['task_id'] or None
            tree = request.form['tree']
            score = []
            otus = []
            if task_id is not None and file is None:
                try:
                    filename = "matrix_" + task_id + ".txt"
                    (score, otus) = open_matrix(filename, otus, score)
                except:
                    flash("task ID was not found in the database. Make sure you pasted the complete ID.")
                    return redirect(request.url)
            elif task_id is None and file is not None:
                (filename, task_id) = upload_file('file')
                (score, otus) = open_matrix(filename, otus, score)
            elif task_id is not None and file is not None:
                try:
                    filename = "matrix_" + task_id + ".txt"
                    (score, otus) = open_matrix(filename, otus, score)
                    flash("Task ID was used because Matrix File was found in the database")
                except:
                    (filename, task_id) = upload_file('file')
                    (score, otus) = open_matrix(filename, otus, score)
                    flash("File was uploaded because task ID was not found")
            else:
                flash("Either upload a file or input a task ID")
                return redirect(request.url)

            out_tree = "tree_"+task_id+".txt"
            q = Queue(connection=redis_connection)
            job = q.enqueue(phylo_tree,
                            job_id=task_id,
                            job_timeout='30m',
                            result_ttl='168h',
                            args=(score, otus, tree, UPLOAD_FOLDER, out_tree))
            return render_template('get_completed_results_form.html', msg=task_id)
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
            q = Queue(connection=redis_connection)
            job = q.enqueue(complete_calc,
                            job_id=task_id,
                            job_timeout='30m',
                            result_ttl='168h',
                            args=(out_align, filename, input_type, align_method, 
                                align_clw_opt, matrix_output, gapdel, model, 
                                tree, UPLOAD_FOLDER, out_tree, plusgap_checked))
            return render_template('get_completed_results_form.html', msg=task_id)
    else:
        return render_template('complete_calc_form.html')

# Website Stuff
@app.route('/')
def index():
    return render_template('index.html')

# # Worker for rq
def run_worker(redis_connection):
    with Connection(redis_connection):
        worker = Worker(app.config['QUEUES'])
        worker.work()

#################################################
# TODO: Get job list and list all finished tasks
# @app.route('/task_list')
# def task_list():
#     filename_list = ()
#     date_created_list = ()
#     registry = registry.FinishedJobRegistry('default', connection=redis)
#     job_ids = registry.get_job_ids() # You can then turn these into Job instances
#     for job_id in job_ids:
#         job = Job.fetch(job_id, connection=redis_connection)
#         sliced =  job.description
#         b_sliced = sliced.split('\'')
#         filename_list.append(b_sliced[3])
#         date_created_list.append(job.created_at)
#     return redirect(request.url)
#################################################

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
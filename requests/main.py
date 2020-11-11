from flask import Flask, request, flash, redirect, url_for, send_from_directory, send_file, jsonify, render_template, abort
from calculation import alignment, distance_matrix, phylo_tree, complete_calc, phylo_tree_score_otus
from werkzeug.utils import secure_filename
from zipfile import ZipFile
from redis import Redis
from rq import Queue, Connection, Worker, registry, cancel_job, get_current_job
from rq.job import Job
from flask_cors import CORS
import datetime, time, os, uuid, pickle, glob, redis, rq_dashboard
import shutil
from functools import wraps

# Function to check for API key
def require_appkey(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.headers['Apikey'] and request.headers['Apikey'] == os.environ['BACKEND_APIKEY']:
            return view_function(*args, **kwargs)
        else:
            abort(401)
    return decorated_function

# Global variables
# UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "/files"
# ZIPPED_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "/zipped"
UPLOAD_FOLDER = "/data/files"
ZIPPED_FOLDER = "/data/zipped"
ALLOWED_EXTENSIONS = {'fasta', 'txt', 'fa'}

app = Flask(__name__)
CORS(app)
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
        otus.append(line_read.pop(0))
        pre_score = line_read.pop(0)
        score.append(list(map(float, pre_score.split(" ")[:-1:])))
    f.close()
    return (score, otus)

def zipFilesInDir(dirName, zipFileName, filter, result_id):
   # create a ZipFile object
   with ZipFile(zipFileName, 'w') as zipObj:
       # Iterate over all the files in directory
       for filename in os.listdir(dirName):
           if filter(filename):
               if filename.endswith('dnd'):
                   continue
               filename_new = filename.replace("_"+result_id, '')
               print(filename)
               # Add file to zip
               zipObj.write(os.path.join(dirName, filename), "./"+filename_new)

# Helper function for allowed files
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# File Upload
# necessary input: 
# file: [select file]
@app.route('/upload', methods=['GET', 'POST'])
@require_appkey
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
@require_appkey
def align(task_id=None, filename=None):
    res = {}
    res['msg'] = ""
    if request.method == 'POST':
        # if request.form['submit_button'] == 'go_back':
        #         return redirect(url_for('index'))
        # elif request.form['submit_button'] == 'calculate':
            (filename, task_id) = upload_file('file')
            if not filename.endswith(('.fasta', '.fa', '.txt')):
            # if not filename.endswith('.fasta'):
                # flash('File format not correct. Choose fasta file')
                # return redirect(request.url)
                res = {'task_id': "None",
                        'msg': "ERROR: File format"}
                return res
            align_method = request.form['align_method']
            input_type = request.form['input_type']
            align_clw_opt = request.form['align_clw_opt']
            out_align = "alignment_"+ task_id +".txt"

            q = Queue(connection=redis_connection)
            job = q.enqueue(alignment,
                            job_id=task_id,
                            job_timeout='3h',
                            result_ttl='168h',
                            args=(out_align, filename, input_type, align_method,  align_clw_opt))
            #return render_template('get_completed_results_form.html', msg=task_id)
            res = {'task_id': task_id,
                    'msg': "Started"}
            return res
    else:
        return render_template('alignment_form.html')

@app.route('/cancel_job', methods=['GET', 'POST'])
@require_appkey
def cancel_job():
    if request.method == 'POST':
        res = {}
        res['result_id'] = request.form['result_id']
        print(res['result_id'])
        job = Job.fetch(res['result_id'], connection=redis_connection)
        try:
            job.cancel()
            # cancel_job(res['result_id'],connection=redis_connection)
            res['msg'] = "Cancelled"
        except:
            res['msg'] = "INFO : Job ID was not found."
        finally:
            return res



@app.route('/task_query', methods=['GET', 'POST'])
@require_appkey
def task_query():

    if request.method == 'POST':
        res = {}
        result_id = request.form['result_id']
        try:
            job = Job.fetch(result_id, connection=redis_connection)
            try:
                i = job.meta['times']
            except:
                i = 0
        except:
            return("INFO : Job ID was not found.")
        if job.get_status() == 'finished':
            res['msg'] = "Finished"
            res['result_id'] = result_id
            return(res)
        elif job.get_status() == 'queued':
            q = Queue(connection=redis_connection)
            current_q = q.get_job_ids()
            index = current_q.index(result_id)
            res['msg'] = f"In queue ({index+1})"
            res['result_id'] = result_id
            return(res)
        elif job.get_status() == 'started':
            res['result_id'] = result_id
            job.meta['times'] = i + 1
            job.save_meta()
            if (job.meta['times'] % 2) == 0:
                res['msg'] = "Running."
            else:
                res['msg'] = "Running.."
            return(res)
        elif job.get_status() == 'failed':            
            res['msg'] = "Failed"
            if 'rq.timeouts.JobTimeoutException' in job.__dict__["exc_info"]:
                res['result_id'] = 'Time limit of 24 hours reached'
            else:
                data = job.__dict__["exc_info"].split("raise")[-1]
                output = data.splitlines()
                output_exception = output[1].split(': ')
                try:
                    res['result_id'] = output_exception[1]
                except:
                    res['result_id'] = output
            return(res)

@app.route('/get_result_completed', methods=['GET', 'POST'])
@require_appkey
def get_result_completed(result_id=None, result_kind=None):
    test = []
    if request.method == 'POST':
        result_id = request.form['result_id']
        result_kind = request.form['result_kind']
        try:
            job = Job.fetch(result_id, connection=redis_connection)
        except:
            flash("The job ID was not found. Make sure you have pasted the full ID")
            return redirect(request.url)
        if job.get_status() == 'finished':
            if result_kind == 'complete':
                result_zip = 'results_' + result_id + '.zip'
                # Check if zip file was generated in a previous step and delete that to avoid duplicates
                if os.path.exists(ZIPPED_FOLDER+"/"+result_zip):
                    os.remove(ZIPPED_FOLDER+"/"+result_zip)
                    zipFilesInDir(UPLOAD_FOLDER, ZIPPED_FOLDER+"/"+result_zip, lambda name : result_id in name, result_id)
                else:
                    zipFilesInDir(UPLOAD_FOLDER, ZIPPED_FOLDER+"/"+result_zip, lambda name : result_id in name, result_id)
                if os.path.exists(ZIPPED_FOLDER+"/"+result_zip):
                    # return send_from_directory(app.config['ZIPPED_FOLDER'], result_zip)
                    send = send_file(app.config['ZIPPED_FOLDER']+"/"+result_zip,as_attachment=True)
                    return send
                    # return send_file(app.config['ZIPPED_FOLDER']+"/"+result_zip,as_attachment=True)
            elif result_kind == 'tree':
                tree_file = "tree_"+result_id+".txt"
                if os.path.exists(UPLOAD_FOLDER+"/"+tree_file):
                    f = open(os.path.join(app.config['UPLOAD_FOLDER'], tree_file), "r")
                    output = f.read().replace('\n', '')
                    f.close()
                    return output
                else:
                    return("Tree file not found. Run the calculation first.")
            else:
                flash("Something went wrong.")
                return redirect(request.url)
        elif job.get_status() == 'queued':
            flash("The job is still in the queue")
            #return "redirect(request.url)"
            return("The job is still in the queue")
        elif job.get_status() == 'started':
            flash("The job is still running")
            #return redirect(request.url)
            return("The job is still running")
        elif job.get_status() == 'failed':
            flash("The job failed. Either it took longer than 30 minutes or the provided file is not correct.")
            #return redirect(request.url)
            return("The job failed.")
    else:
        return render_template('get_completed_results_form.html')

# necessary input: 
# file: or task ID
# task_id: from previous step
# plusgap: "checked" / ""
# gapdel: "comp" / "pair"
# input_type: nuc or ami [not necessary for mafft]
# model: P, PC, JC or K2P
@app.route('/matrix', methods=['GET', 'POST'])
@require_appkey
def matrix(task_id=None):
    res = {}
    res['msg'] = ""
    if request.method == 'POST':
        # file = request.files['file'] or None
        try:
            file = request.files['file']
        except:
            file = None
        try:
            task_id = request.form['task_id']
            filename = "alignment_" + task_id + ".txt"
            f = open(os.path.join(app.config['UPLOAD_FOLDER'], filename), "r")
            f.close()
        except:
            task_id = None
        if task_id is not None and file is None:
            filename = "alignment_" + task_id + ".txt"
            try:
                f = open(os.path.join(app.config['UPLOAD_FOLDER'], filename), "r")
                f.close()
            except:
                #flash("task ID was not found in the database. Make sure you pasted the complete ID.")
                #return redirect(request.url)
                res = {'task_id': "None",
                        'msg': "INFO : Task ID was not found in the database. Make sure you pasted the complete ID."}
                return res
        elif task_id is None and file is not None:
            (filename, task_id) = upload_file('file')
        elif task_id is not None and file is not None:
            try:
                filename = "alignment_" + task_id + ".txt"
                f = open(os.path.join(app.config['UPLOAD_FOLDER'], filename), "r")
                f.close()
                #print("Task ID was used because Matrix File was found in the database")
                res = { 'msg': "INFO : Task ID was used because Matrix File was found in the database"}
            except:
                (filename, task_id) = upload_file('file')
                #print("File was uploaded because task ID was not found")
                res = { 'msg': "INFO : File was uploaded because task ID was not found"}
        else:
            # flash('Choose task ID or upload a file to proceed')
            # return redirect(request.url)
            res = {'task_id': "None",
                        'msg': "INFO : Either upload a file or input a task ID"}
            return res
            
        # if request.form.get("plusgap"):
        #     plusgap_checked = "checked"
        # else:
        #     plusgap_checked = "not_checked"
        plusgap_checked = request.form["plusgap"]
        gapdel = request.form.get("gapdel", None)
        input_type = request.form['input_type']
        model = request.form['model']
        matrix_output = "matrix_"+task_id+".txt"

        q = Queue(connection=redis_connection)
        job = q.enqueue(distance_matrix,
                        job_id=task_id,
                        job_timeout='3h',
                        result_ttl='168h',
                        args=(filename, matrix_output, gapdel, 
                            input_type, model, plusgap_checked))
        #return render_template('get_completed_results_form.html', msg=task_id)
        if res['msg'] == '':
            res['msg'] = "Started"
        
        res['task_id'] = task_id
        return res
    else:
        return render_template('distance_matrix_form.html')

# necessary input: 
# score: [file name]
# otus: [file name]
# task_id: [if files are not specified]
# tree: nj or upgma
@app.route('/tree', methods=['GET', 'POST'])
@require_appkey
def tree():
    res = {}
    res['msg'] = ""
    if request.method == 'POST':
        try:
            file = request.files['file']
        except:
            file = None
        task_id = request.form['task_id'] or None
        tree = request.form['tree']
        # score = []
        # otus = []
        # if task_id is not None and file is None:
        #     try:
        #         filename = "matrix_" + task_id + ".txt"
        #         (score, otus) = open_matrix(filename, otus, score)
        #     except:
        #         # flash("task ID was not found in the database. Make sure you pasted the complete ID.")
        #         # return redirect(request.url)
        #         res = {'task_id': "None",
        #                 'msg': "INFO : Task ID was not found in the database. Make sure you pasted the complete ID."}
        #         return res
        # elif task_id is None and file is not None:
        #     (filename, task_id) = upload_file('file')
        #     try:
        #         (score, otus) = open_matrix(filename, otus, score)
        #     except:
        #         raise Exception("No valid matrix")
        # elif task_id is not None and file is not None:
        #     try:
        #         filename = "matrix_" + task_id + ".txt"
        #         (score, otus) = open_matrix(filename, otus, score)
        #         #flash("Task ID was used because Matrix File was found in the database")
        #         res = { 'msg': "INFO : Task ID was used because Matrix File was found in the database"}
        #     except:
        #         (filename, task_id) = upload_file('file')
        #         (score, otus) = open_matrix(filename, otus, score)
        #         #flash("File was uploaded because task ID was not found")
        #         res = { 'msg': "INFO : File was uploaded because task ID was not found"}
        # else:
        #     flash("Either upload a file or input a task ID")
        #     return redirect(request.url)
        #     res = {'task_id': "None",
        #                 'msg': "INFO : Either upload a file or input a task ID"}
        #     return res
        (filename, task_id) = upload_file('file')
        out_tree = "tree_"+task_id+".txt"
        q = Queue(connection=redis_connection)
        # job = q.enqueue(phylo_tree,
        #                 job_id=task_id,
        #                 job_timeout='30m',
        #                 result_ttl='168h',
        #                 args=(score, otus, tree, UPLOAD_FOLDER, out_tree))
        job = q.enqueue(phylo_tree_score_otus,
                        job_id=task_id,
                        job_timeout='3h',
                        result_ttl='168h',
                        args=(filename, tree, UPLOAD_FOLDER, out_tree))
        # return render_template('get_completed_results_form.html', msg=task_id)
        if res['msg'] == '':
            res['msg'] = "Started"
        
        res['task_id'] = task_id
        return res
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
# model: P, PC, JC or K2P
# tree: nj or upgma

@app.route('/complete', methods=['GET', 'POST'])
@require_appkey
def complete():
    res = {}
    res['msg'] = ""
    if request.method == 'POST':
        align_method = request.form['align_method']
        try:
            (filename, task_id) = upload_file('file')
        except:
            res = {'task_id': "File format",
                    'msg': "Error"}
            return res
        if not filename.endswith(('.fasta', '.fa', '.txt')):
            flash('File format not correct. Choose fasta file')
            # return redirect(request.url)
            res = {'task_id': "File format",
                    'msg': 'Error'}
            return res
        input_type = request.form['input_type']
        # 'null' if MAFFT is selected because it doesn't really need it. Just used this step to keep the code working
        if input_type == 'null':
            input_type = 'nuc'
        align_clw_opt = request.form['align_clw_opt']
        # if request.form.get("plusgap"):
        #     plusgap_checked = "checked"
        # else:
        #     plusgap_checked = "not_checked"
        plusgap_checked = request.form["plusgap"]
        gapdel = request.form.get("gapdel", None)
        model = request.form['model']
        tree = request.form['tree']

        out_align = "alignment_"+ task_id +".txt"
        matrix_output = "matrix_"+task_id+".txt"
        out_tree = "tree_"+task_id+".txt"
        q = Queue(connection=redis_connection)
        if align_method == "None":
            print("This is:", filename)
            if filename == 'alignment_'+task_id+'.txt':
            # if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
                print("WE PASS")
                pass
            else:
                print("WE COPY")
                shutil.copy(os.path.join(app.config['UPLOAD_FOLDER'], filename), os.path.join(app.config['UPLOAD_FOLDER'], out_align))
            # try:
            #     f = open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # except:
            #     shutil.copy(os.path.join(app.config['UPLOAD_FOLDER'], filename), os.path.join(app.config['UPLOAD_FOLDER'], out_align))
        job = q.enqueue(complete_calc,
                        job_id=task_id,
                        job_timeout='3h',
                        result_ttl='168h',
                        args=(out_align, filename, input_type, align_method, 
                            align_clw_opt, matrix_output, gapdel, model, 
                            tree, UPLOAD_FOLDER, out_tree, plusgap_checked))
        if res['msg'] == '':
            res['msg'] = 'Started'
        res['task_id'] = task_id
        return res
    else:
        return render_template('complete_calc_form.html')

# Website Stuff
@app.route('/')
@require_appkey
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
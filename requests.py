from flask import Flask, request, flash, redirect, url_for, send_from_directory, jsonify
from calculation import alignment
from werkzeug.utils import secure_filename
import datetime, time, os, uuid

# Global variables
UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + "/files"
ALLOWED_EXTENSIONS = {'fasta'}

app = Flask(__name__)
app.secret_key = "Nj#z2L86|!'=Cw&CG"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return('Blank Page. To be filled.')

# Helper function for allowed files
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# File Upload
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
            #raise Exception('No file provided')
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
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

#######################################
# What if the user closes the window? #
# Is this function still finished?    #
#######################################
@app.route('/alignment', methods=['GET', 'POST'])
def align():
    if request.method == 'POST':
        (filename, task_id) = upload_file()
        if not filename.endswith('.fasta'):
            flash('File format not correct. Choose fasta file')
            return redirect(request.url)
        print(filename)
        align_method = request.form['align_method']
        input_type = request.form['input_type']
        timestamp = datetime.datetime.today().strftime("%Y-%m-%d-%H-%M-%S")
        out_align = "align"+ task_id +".txt"
        print(out_align)

        alignment(out_align, filename=filename, input_type=input_type, align=align_method, align_clw_opt="")
        send_from_directory(app.config['UPLOAD_FOLDER'],out_align)
        result = {
            "jobID": task_id,
            "filename": filename
        }
        return jsonify(result)
    else:
        return 'Use POST'

@app.route('/get_result', methods=['GET', 'POST'])
def uploaded_file():
    if request.method == 'POST':
        result_id = request.form['result_id']
        upload_file = "align"+result_id+".txt"
        print(upload_file)
        if os.path.exists(UPLOAD_FOLDER+"/"+upload_file):
            return send_from_directory(app.config['UPLOAD_FOLDER'], upload_file)
        else:
            return redirect(request.url)
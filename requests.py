from flask import Flask, request, flash, redirect, url_for
from calculation import alignment
from werkzeug.utils import secure_filename
import datetime, time, os

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
            return ('No file')
            #return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return filename
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

# After file upload, remove empty spaces [!secure_filename does that!] and create UUID number
# provide user with that UUID number for later pull request of results
# add UUID to provided file name
# 

@app.route('/alignment', methods=['GET', 'POST'])
def align():
    if request.method == 'POST':
        filename = upload_file()
        align_method = request.form['align_method']
        timestamp = datetime.datetime.today().strftime("%Y-%m-%d-%H-%M-%S")
        out_align = timestamp + "align.txt"
        #--filename small.fasta --type nuc --align clustalw --model P --gapdel comp --tree nj
        alignment(out_align, filename=filename, d="DNA", align=align_method, align_clw_opt="")
        return 'Finished alignment'
    else:
        return 'Use POST'
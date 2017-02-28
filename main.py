from flask import Flask, request, render_template, flash, redirect, send_file, abort, jsonify
from werkzeug.utils import secure_filename
import os
from flask_api import status

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['jpg','png','tiff','jpeg'])
FORM_PERSON_NAME = 'person_name'
FORM_AADHAR_NAME = 'aadhar_file'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # check if the post request has the file part
        file_name = FORM_AADHAR_NAME
        if file_name not in request.files:
            print("no file part")
            return redirect(request.url)
        file = request.files[file_name]
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Read aadhar card barcode
            from read_aadhar import read_aadhar
            data = read_aadhar(file)
            import json
            adata = json.dumps(data)
            return render_template('index.html', text=adata)

    return render_template('index.html')


@app.route("/authorize", methods=['POST'])
def decode_aadhar():
 if request.method == 'POST':
        # check if the post request has the file part
        file_name = FORM_AADHAR_NAME
        if file_name not in request.files:
            print("no file part")
            return jsonify({'error': 'No Aadhar file is provided'}), 400
        file = request.files[file_name]
        if file.filename == '':
            return jsonify({'error': 'No Aadhar file is provided'}), 400
        if file and allowed_file(file.filename) and request.form.get(FORM_PERSON_NAME):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            person_name = request.form.get(FORM_PERSON_NAME)
            # Read aadhar card barcode
            from read_aadhar import read_aadhar
            data = read_aadhar(file)
            is_allowed = authorize(data['name'], person_name)
            if is_allowed:
                data['authorized'] = True
                return jsonify(data)
            else:
                return jsonify({'error': 'You are not authorized', 'authorized': False}), 403


def authorize(aadhar_data, person_name):
    aname_dict = parse_name(aadhar_data)
    pname_dict = parse_name(person_name)
    return ( aname_dict['FirstName'].lower() == pname_dict['FirstName'].lower() ) and ( aname_dict['LastName'].lower() == pname_dict['LastName'].lower() )



def parse_name(name):
    import re    
    first_name, last_name = name.split(' ', 1)
    first_initial = re.search("^[A-Z.]+", first_name).group()
    if not first_initial.endswith("."):
        first_initial += "."
    return {"FirstName": first_name,
            "FirstInitial": first_initial,
            "LastName": last_name}

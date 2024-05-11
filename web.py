from crypt import methods
from flask import Flask, render_template, jsonify, request, send_file, Response
from werkzeug.utils import secure_filename
import os
from main import *
#import magic
import urllib.request
from datetime import datetime
   
app = Flask(__name__)
       
app.secret_key = "flsldfj399dksdf-fj39fls.vicsla92kdan-mcd83jkksdh"

#Reference to server directory:
from pathlib import Path
THIS_FOLDER = Path(__file__).parent.resolve()

UPLOAD_FOLDER = THIS_FOLDER / "uploads"
DOWNLOAD_FOLDER = THIS_FOLDER / "files"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
   
ALLOWED_EXTENSIONS = set(['xlsx'])
   
def allowed_file(filename):
 return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def read_local_plain_text(file_name):
    with open(file_name, "r") as file:
        data = file.read()
    return data.replace("\n", "|")

def read_local_json(json_file_name):
        json_file = open(json_file_name, "r")
        data = json_file.read()
        json_file.close()
        return data

@app.route('/api/metadatos')
def api_returnMetadatos():
   if request.method == "GET":
        token = request.args.get('token')
        if not token or token != app.secret_key:
            return json.dumps({'success':False, 'reason' : 'Not authorized'}), 401, {'ContentType':'application/json'}
        data = read_local_json(os.path.join(app.config['DOWNLOAD_FOLDER'],'1_metadatos.json'))
        return data, 200, {'ContentType':'application/json'}    
 
@app.route('/metadatos')
def returnMetadatos():
    downloads = os.path.join(app.root_path, app.config['DOWNLOAD_FOLDER'])
    return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'],'1_metadatos.json'), as_attachment=True)

@app.route('/api/catalogoMetadatosHomologados')
def api_returnCatalogoMetadatosHomologados():
   if request.method == "GET":
        token = request.args.get('token')
        if not token or token != app.secret_key:
            return json.dumps({'success':False, 'reason' : 'Not authorized'}), 401, {'ContentType':'application/json'}
        data = read_local_json(os.path.join(app.config['DOWNLOAD_FOLDER'],'1_catalogo_metadatos_homologados.json'))
        return data, 200, {'ContentType':'application/json'}    

@app.route('/catalogoMetadatosHomologados')
def returnCatalogoMetadatosHomologados():
    downloads = os.path.join(app.root_path, app.config['DOWNLOAD_FOLDER'])
    return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'],'1_catalogo_metadatos_homologados.json'), as_attachment=True)
 
@app.route('/api/metadatosNoValidos')
def api_returnMetadatosNoValidos():
   if request.method == "GET":
        token = request.args.get('token')
        if not token or token != app.secret_key:
            return json.dumps({'success':False, 'reason' : 'Not authorized'}), 401, {'ContentType':'application/json'}
        data = read_local_json(os.path.join(app.config['DOWNLOAD_FOLDER'],'1_metadatos_no_validos.json'))
        return data, 200, {'ContentType':'application/json'} 

@app.route('/metadatosNoValidos')
def returnMetadatosNoValidos():
    downloads = os.path.join(app.root_path, app.config['DOWNLOAD_FOLDER'])
    return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'],'1_metadatos_no_validos.json'), as_attachment=True)

@app.route('/api/catalogoSistemas')
def api_returnCatalogoSistemas():
   if request.method == "GET":
        token = request.args.get('token')
        if not token or token != app.secret_key:
            return json.dumps({'success':False, 'reason' : 'Not authorized'}), 401, {'ContentType':'application/json'}
        data = read_local_json(os.path.join(app.config['DOWNLOAD_FOLDER'],'1_catalogo_sistemas.txt'))
        return data, 200, {'ContentType':'application/json'} 

@app.route('/')
def main():
    return render_template('index.html')

@app.route("/api/create", methods=["GET"])
def api_create():
    if request.method == "GET":
        token = request.args.get('token')
        if not token or token != app.secret_key:
            return json.dumps({'success':False, 'reason' : 'Not authorized'}), 401, {'ContentType':'application/json'}
        doMainReadingFromGoogle()
        return json.dumps({'success':True, 'reason' : 'File generated ok'}), 200, {'ContentType':'application/json'}

@app.route("/create", methods=["GET"])
def create():
    if request.method == "GET":
        doMainReadingFromGoogle()
        return json.dumps({'success':True, 'reason' : 'File generated ok'}), 200, {'ContentType':'application/json'}


# create a route to get the contents of the sistemasGestorContenido.txt file
@app.route('/api/sistemas')
def api_sistemas():
    if request.method == "GET":
        token = request.args.get('token')
        if not token or token != app.secret_key:
            return json.dumps({'success':False, 'reason' : 'Not authorized'}), 401, {'ContentType':'application/json'}
        data = read_local_plain_text(SISTEMAS_FILE)
        return data, 200, {'ContentType':'application/json'}

# create a post route that will receive a param called "sistema", will read the file sistemasGestorContenido.txt remove the sistema that matches with the param and write
# the new content to the file

@app.route('/api/deleteSistema', methods=["POST"])
def api_sistemas_post():
    if request.method == "POST":
        token = request.args.get('token')
        if not token or token != app.secret_key:
            return json.dumps({'success':False, 'reason' : 'Not authorized'}), 401, {'ContentType':'application/json'}
        sistema = request.form.get('sistema')
        if not sistema:
            return json.dumps({'success':False, 'reason' : 'No sistema provided'}), 400, {'ContentType':'application/json'}
        data = read_local_plain_text(SISTEMAS_FILE)
        # parse the data, it's pipe separated, put it in a list, remove the sistema and write it back to the file
        parsed_data = data.split("|");
        if sistema in parsed_data:
            parsed_data.remove(sistema)
            # write the new data to the file, remove the pipes and write one element per line
            data = "\n".join(parsed_data)
            with open(SISTEMAS_FILE, "w") as file:
                file.write(data)
            return json.dumps({'success':True, 'reason' : 'Sistema removed'}), 200, {'ContentType':'application/json'}
        else:
            return json.dumps({'success':False, 'reason' : 'Sistema not found'}), 404, {'ContentType':'application/json'}

@app.route("/upload",methods=["POST","GET"])
def upload():

    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        now = datetime.now()
          
        if file and allowed_file(file.filename):
           file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
           print('File successfully uploaded ' + file.filename + ' to the server!')
           doMain(os.path.join(app.config['UPLOAD_FOLDER'],file.filename))
        else:
           print('Solo archivos excel xlsx') 
        msg = 'Archivo recibido'    
    return jsonify(msg)

# create 'api/createSistema' route that will receive a param called "sistema" and will write it to the file sistemasGestorContenido.txt
@app.route('/api/createSistema', methods=["POST"])
def api_create_sistema():
    if request.method == "POST":
        token = request.args.get('token')
        if not token or token != app.secret_key:
            return json.dumps({'success':False, 'reason' : 'Not authorized'}), 401, {'ContentType':'application/json'}
        sistema = request.form.get('sistema')
        if not sistema:
            return json.dumps({'success':False, 'reason' : 'No sistema provided'}), 400, {'ContentType':'application/json'}
        data = read_local_plain_text(SISTEMAS_FILE)
        # parse the data, it's pipe separated, put it in a list, add the sistema and write it back to the file
        parsed_data = data.split("|");
        if sistema not in parsed_data:
            parsed_data.append(sistema)
            # write the new data to the file, remove the pipes and write one element per line
            data = "\n".join(parsed_data)
            with open(SISTEMAS_FILE, "w") as file:
                file.write(data)
            return json.dumps({'success':True, 'reason' : 'Sistema added'}), 200, {'ContentType':'application/json'}
        else:
            return json.dumps({'success':False, 'reason' : 'Sistema already exists'}), 400, {'ContentType':'application/json'}

@app.route('/api/archivo')
def api_archivo():
   if request.method == "GET":
        downloads = os.path.join(app.root_path, app.config['DOWNLOAD_FOLDER'])
        return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'],'Archive.zip'), as_attachment=True)
 
if __name__ == "__main__":
    app.run(debug=True)
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
       
 
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
   
ALLOWED_EXTENSIONS = set(['xlsx'])
   
def allowed_file(filename):
 return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
 
if __name__ == "__main__":
    app.run(debug=True)
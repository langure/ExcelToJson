from crypt import methods
from flask import Flask, render_template, jsonify, request, send_file
from werkzeug.utils import secure_filename
import os
from main import *
#import magic
import urllib.request
from datetime import datetime
   
app = Flask(__name__)
       
app.secret_key = "gsdfgsdfgser454rsgdfgserg"
       
 
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
   
ALLOWED_EXTENSIONS = set(['xlsx'])
   
def allowed_file(filename):
 return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
@app.route('/metadatos')
def returnMetadatos():
    downloads = os.path.join(app.root_path, app.config['DOWNLOAD_FOLDER'])
    return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'],'1_metadatos.json'), as_attachment=True)

@app.route('/catalogoMetadatosHomologados')
def returnCatalogoMetadatosHomologados():
    downloads = os.path.join(app.root_path, app.config['DOWNLOAD_FOLDER'])
    return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'],'1_catalogo_metadatos_homologados.json'), as_attachment=True)
 
@app.route('/metadatosNoValidos')
def returnMetadatosNoValidos():
    downloads = os.path.join(app.root_path, app.config['DOWNLOAD_FOLDER'])
    return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'],'1_metadatos_no_validos.json'), as_attachment=True)

@app.route('/')
def main():
    return render_template('index.html')

@app.route("/create", methods=["GET"])
def create():
    if request.method == "GET":
        doMainReadingFromGoogle()
        return jsonify("ok")
        
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
from flask import Flask, render_template, jsonify, request
from werkzeug.utils import secure_filename
import os
#import magic
import urllib.request
from datetime import datetime
   
app = Flask(__name__)
       
app.secret_key = "gsdfgsdfgser454rsgdfgserg"
       
 
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
   
ALLOWED_EXTENSIONS = set(['xlsx'])
   
def allowed_file(filename):
 return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
 
@app.route('/')
def main():
    return render_template('index.html')
       
@app.route("/upload",methods=["POST","GET"])
def upload():

    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        now = datetime.now()
          
        if file and allowed_file(file.filename):
           file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
           print('File successfully uploaded ' + file.filename + ' to the database!')
        else:
           print('Solo archivos excel xlsx') 
        msg = 'Archivo recibido'    
    return jsonify(msg)
 
if __name__ == "__main__":
    app.run(debug=True)
#!/data/data/com.termux/files/usr/bin/env python
import argparse
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os

UPLOAD_FOLDER = os.getcwd()  # Set default upload folder to the present working directory

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def parse_arguments():
    parser = argparse.ArgumentParser(description='Simple file upload server with options.')
    parser.add_argument('-d', '--directory', default=UPLOAD_FOLDER, help='Directory for storing uploaded files (default: current directory)')
    return parser.parse_args()

def setup_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Upload directory '{directory}' created.")

@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    filename = file.filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    args = parse_arguments()
    app.config['UPLOAD_FOLDER'] = args.directory
    setup_directory(app.config['UPLOAD_FOLDER'])
    app.run(host='0.0.0.0', port=8080, debug=True)

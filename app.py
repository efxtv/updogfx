#!/data/data/com.termux/files/usr/bin/env python

import argparse
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import urllib.parse
import socket
import logging
import subprocess
import re

# About : inspired by updog we named it updogfx Date 18/05/2025
# Supports termux and most of the linux based os having ssh and bash shell installed
# Version 2.0
# Installation 
# requirements.txt
# Flask
# or pip install Flask
# python app.py
# Python to exe 
# pip install pyinstaller
# pyinstaller --onefile --add-data "templates;templates" app.py

# Suppress Flask and Werkzeug logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.CRITICAL)

cli = logging.getLogger('flask.cli')
cli.setLevel(logging.CRITICAL)

# Flask setup
UPLOAD_FOLDER = os.getcwd()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def parse_arguments():
    parser = argparse.ArgumentParser(description='Simple file upload server with options.')
    parser.add_argument('-d', '--directory', default=UPLOAD_FOLDER,
                        help='Directory to store uploaded files (default: current directory)')
    return parser.parse_args()

def setup_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"[+] Upload directory created: {directory}")

def save_file(file, filename):
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or request.files['file'].filename == '':
        return redirect(request.url)
    file = request.files['file']
    filename = urllib.parse.quote(file.filename)
    save_file(file, filename)
    print(f"[+] File uploaded: {urllib.parse.unquote(filename)}")
    return redirect(url_for('index'))

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    filename = urllib.parse.unquote(filename)
    print(f"[+] File downloaded: {filename}")
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def linkgens():
    try:
        # Start the SSH process
        process = subprocess.Popen(
            ['ssh', '-o', 'StrictHostKeyChecking=no', '-R', '80:127.0.0.1:8080', 'serveo.net'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Read output line by line
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                # Search for a serveo.net URL
                match = re.search(r'https://[a-zA-Z0-9]+\.serveo\.net', output)
                if match:
                    print(f"\nUpload on: {match.group(0)}\n")
                    break

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    args = parse_arguments()
    app.config['UPLOAD_FOLDER'] = args.directory
    setup_directory(app.config['UPLOAD_FOLDER'])

    # Get local IP
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
    except socket.gaierror:
        local_ip = "127.0.0.1"

    port = 8080
    print(f"\nUpload on: http://{local_ip}:{port}")

    # Start Serveo reverse tunnel and display link
    linkgens()

    # Start Flask app
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False, threaded=True)

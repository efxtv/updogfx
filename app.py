#!/usr/bin/env python3

import argparse
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import urllib.parse
import socket
import logging
import subprocess
import re
import sys
import threading
import time
from jinja2 import FileSystemLoader # Corrected: Ensure FileSystemLoader is imported

# About : inspired by updog we named it updogfx Date 2/07/2025
# Version 2.1 (Finalized output and cloudflared log parsing)

# Suppress Flask and Werkzeug logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.CRITICAL)

cli = logging.getLogger('flask.cli')
cli.setLevel(logging.CRITICAL)

# Suppress Flask's startup banner explicitly for app.run()
try:
    import flask.cli
    flask.cli.show_server_banner = lambda *args: None
except ImportError:
    # Fallback for older Flask versions if the attribute doesn't exist
    pass

# Base directory of this app.py file
basedir = os.path.abspath(os.path.dirname(__file__))

# Setup Flask app
app = Flask(__name__)

# Configure Jinja2 loader
app.jinja_loader = FileSystemLoader(os.path.join(basedir, "templates"))

UPLOAD_FOLDER = os.getcwd()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define a path for the cloudflared log file
CLOUDFLARED_LOG_DIR = os.path.join(os.path.expanduser("~"), ".cloudflared_logs")
CLOUDFLARED_LOG_FILE = os.path.join(CLOUDFLARED_LOG_DIR, "updogfx_cf.log")

def parse_arguments():
    parser = argparse.ArgumentParser(description='Simple file upload server with options.')
    parser.add_argument('-d', '--directory', default=UPLOAD_FOLDER,
                        help='Directory to store uploaded files (default: current directory)')
    return parser.parse_args()

def setup_directory(directory):
    """Ensures the upload and cloudflared log directories exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)

    if not os.path.exists(CLOUDFLARED_LOG_DIR):
        os.makedirs(CLOUDFLARED_LOG_DIR)

def save_file(file, filename):
    """Saves an uploaded file to the configured UPLOAD_FOLDER."""
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

@app.route('/')
def index():
    """Renders the main page showing uploaded files."""
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles file uploads."""
    if 'file' not in request.files or request.files['file'].filename == '':
        return redirect(request.url)
    file = request.files['file']
    filename = urllib.parse.quote(file.filename)
    save_file(file, filename)
    flush_print(f"[+] File uploaded: {urllib.parse.unquote(filename)}")
    return redirect(url_for('index'))

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serves uploaded files for download."""
    filename = urllib.parse.unquote(filename)
    flush_print(f"[+] File downloaded: {filename}")
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def linkgens(port):
    """
    Initiates a Cloudflare Tunnel and extracts the public URL from its log file.
    Runs cloudflared in the background and suppresses its direct output.
    """
    try:
        # Clear previous log file content if it exists
        if os.path.exists(CLOUDFLARED_LOG_FILE):
            with open(CLOUDFLARED_LOG_FILE, 'w') as f:
                f.truncate(0)

        # Start cloudflared in the background, logging to a file
        # Redirect stdout and stderr to /dev/null to keep console clean
        FNULL = open(os.devnull, 'w')
        subprocess.Popen(
            ['cloudflared', 'tunnel', '-url', f'http://localhost:{port}', '--logfile', CLOUDFLARED_LOG_FILE],
            stdout=FNULL,
            stderr=FNULL,
            start_new_session=True # Detach from current session
        )
        FNULL.close()

        # Give cloudflared time to establish the tunnel and write the URL to the log
        time.sleep(10)

        public_url = None
        if os.path.exists(CLOUDFLARED_LOG_FILE):
            with open(CLOUDFLARED_LOG_FILE, 'r') as f:
                log_content = f.read()
            match = re.search(r'(https?://[a-zA-Z0-9-]+\.trycloudflare\.com)', log_content)
            if match:
                public_url = match.group(1)

        if public_url:
            flush_print(f"[+] Public server on: {public_url}")
        else:
            # Provide error message if URL not found, suggest checking log
            flush_print("[-] Could not find Cloudflare Tunnel public URL in log file.")
            flush_print(f"    Check log file for errors: {CLOUDFLARED_LOG_FILE}")

    except FileNotFoundError:
        flush_print("[-] Error: 'cloudflared' command not found.")
        flush_print("    Please install Cloudflare Tunnel (cloudflared) and ensure it's in your system's PATH.")
        flush_print("    Installation instructions: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-run/")
    except Exception as e:
        flush_print(f"[-] An unexpected error occurred with cloudflared: {e}")

def flush_print(message):
    """Prints a message immediately to the console."""
    print(message, flush=True)

def main():
    """Main function to parse arguments, setup, and run the Flask app."""
    args = parse_arguments()
    app.config['UPLOAD_FOLDER'] = args.directory
    setup_directory(app.config['UPLOAD_FOLDER']) # This call is now silent for directory creation

    try:
        local_ip = socket.gethostbyname(socket.gethostname())
    except socket.gaierror:
        local_ip = "127.0.0.1" # Fallback if hostname resolution fails

    port = 8080

    # Desired startup output
    flush_print("[+] Updogfx v2.1 by EFXTv")
    flush_print(f"[+] Local access on: http://{local_ip}:{port}")

    # Start cloudflared tunnel creation in a separate daemon thread
    # It will print its URL to the console when found
    tunnel_thread = threading.Thread(target=linkgens, args=(port,), daemon=True)
    tunnel_thread.start()

    # Start the Flask web server
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=True)

if __name__ == '__main__':
    main()

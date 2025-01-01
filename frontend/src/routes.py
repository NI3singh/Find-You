# routes.py
from flask import render_template, send_from_directory, current_app
from app import app

@app.route('/')
def index():
    """Render the main upload page"""
    return render_template('index.html')

@app.route('/camera/<event_id>')
def gallery(event_id):
    """Render the camera capture page for a specific gallery"""
    return render_template('camera.html')

@app.route('/result/<resultId>')
def result(resultId):
    """Render the result page for a specific result."""
    return render_template('result.html', resultId=resultId)

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    """Serve uploaded files (with proper authentication in production)"""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

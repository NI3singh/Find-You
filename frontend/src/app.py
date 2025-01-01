
# app.py
from flask import Flask
from flask_cors import CORS
import os
from werkzeug.middleware.proxy_fix import ProxyFix


app = Flask(__name__,
    static_folder='static',
    template_folder='templates'
)

# Configuration
app.config.update(
    SECRET_KEY=os.urandom(24),
    MAX_CONTENT_LENGTH=3000 * 1024 * 1024,
    MAX_CONTENT_LENGTH_PER_FILE=50 * 1024 * 1024,  # 50MB per file
    ALLOWED_EXTENSIONS={'png', 'jpg', 'jpeg','JPG','.heic'},
    FACE_RECOGNITION_THRESHOLD=0.5,
    TEMPORARY_FOLDER='temp'
)

# Ensure temporary directorie exist
os.makedirs(app.config['TEMPORARY_FOLDER'], exist_ok=True)

# Enable CORS
CORS(app)

# Handle proxy headers
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

# Import routes after app initialization to avoid circular imports
from routes import *
from api import *

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


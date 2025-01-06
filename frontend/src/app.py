from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import os
from flask_login import LoginManager
from flask_security import Security, SQLAlchemyUserDatastore
from models import db, User, Role




# Initialize the Flask app
app = Flask(
    __name__,
    static_folder='static',
    template_folder='templates'
)

basedir = os.path.abspath(os.path.dirname(__file__))
# Configuration
app.config.update(
    SESSION_COOKIE_SECURE=False,
    REMEMBER_COOKIE_SECURE=False,
    USE_SESSION_FOR_NEXT=True,
    SECRET_KEY=os.urandom(24),
    SECURITY_PASSWORD_SALT='nitin123',
    SQLALCHEMY_DATABASE_URI=f"sqlite:///{os.path.join(basedir, 'webapp.db')}",  # SQLite database for user authentication
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SECURITY_PASSWORD_HASH='bcrypt',
    SECURITY_REGISTERABLE=False,
    SECURITY_SEND_REGISTER_EMAIL=False,
    SECURITY_UNAUTHORIZED_VIEW='/login',
    MAX_CONTENT_LENGTH=3000 * 1024 * 1024,
    MAX_CONTENT_LENGTH_PER_FILE=50 * 1024 * 1024,  # 50MB per file
    ALLOWED_EXTENSIONS={'png', 'jpg', 'jpeg', 'JPG', '.heic'},
    FACE_RECOGNITION_THRESHOLD=0.5,
    TEMPORARY_FOLDER='temp',
    SECURITY_DEFAULT_REMEMBER_ME=True
)

# Ensure temporary directories exist
os.makedirs(app.config['TEMPORARY_FOLDER'], exist_ok=True)

# Initialize Flask extensions
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)


# Import db and models
from models import db, User

# Initialize database with app
db.init_app(app)

# Initialize Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Import routes and APIs after app initialization
from routes import *
from api import *


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

# routes.py
from flask import render_template, send_from_directory, current_app, redirect, url_for, request, flash
from app import app, db
from flask_security import login_user, logout_user, current_user, login_required
from models import User
from werkzeug.security import check_password_hash

# routes.py
from flask import render_template, send_from_directory, current_app, redirect, url_for, request, flash
from app import app, db
from flask_security import login_user, logout_user, current_user, login_required
from models import User
from werkzeug.security import check_password_hash


@app.route('/')
@login_required
def index():
    return render_template('index.html')


@app.route('/camera/<event_id>')
def camera(event_id):
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

@app.route('/login', methods=['GET', 'POST'])
@login_required
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))  # Redirect to the main page after login
        else:
            flash("Invalid email or password", "error")
            return render_template('login.html')

    return render_template('login.html')  # Render login page for GET requests


# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/protected')
@login_required
def protected():
    return f'Hello {current_user.email}'
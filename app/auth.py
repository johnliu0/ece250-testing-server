import sys
import uuid
from flask import (
    abort,
    Blueprint,
    current_app as flask_app,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
    g)
from bson.json_util import dumps
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from models.user import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@flask_app.before_request
def provide_auth():
    """Provides authentication details in g.user."""
    if 'auth' in session:
        g.auth = session['auth']
    else:
        g.auth = { 'isAuthenticated': False }

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_query = User.objects.raw({ 'email': email })
        # check if user exists
        try:
            user = User.objects.get({ 'email' : email })
            # check if password is correct
            if check_password_hash(user.password_hash, password):
                session['auth'] = {
                    'isAuthenticated': True,
                    'user': {
                        'email': user.email
                    }
                }

                print(f'INFO: User {email} logged in')
                return redirect(url_for('index'))
            else:
                return render_template('auth/login.html', error='Incorrect password')
        except User.DoesNotExist:
            return render_template('auth/login.html', error='User does not exist')

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('auth/signup.html')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']

        # ensure password meets minimum requirements
        if len(password) == 0:
            return render_template('auth/signup.html', error='Password cannot be empty')
        if len(password) < 6:
            return render_template('auth/signup.html', error='Password must be at least 6 characters long')
        if password != confirm_password:
            return render_template('auth/signup.html', error='Passwords do not match')

        # check if the email is already in use
        user_query = User.objects.raw({ 'email': email })
        if user_query.count() != 0:
            return render_template('auth/signup.html', error='Email already in use')

        # create a new user in the database
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            validation_token=str(uuid.uuid1()),
            submissions=[]
        ).save()

        print(f'INFO: User {email} signed up')

        return render_template('auth/signupsuccess.html')

@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    if 'auth' in session:
        session['auth'] = { 'isAuthenticated': False }
    return render_template('auth/logoutsuccess.html')

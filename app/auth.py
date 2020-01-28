import sys
from flask import (
    abort,
    Blueprint,
    current_app as app,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for)
from bson.json_util import dumps
from werkzeug.security import check_password_hash, generate_password_hash
import app.db
from app.models.user import User, create_user

bp = Blueprint('auth', __name__, url_prefix='/auth')

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
                return redirect(url_for('index'))
            else:
                return render_template('auth/login.html', error='Incorrect password')
        except User.DoesNotExist:
            return render_template('auth/login.html', error='User does not exist')

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    app.logger.info('signup!')
    if request.method == 'GET':
        return render_template('auth/signup.html')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']

        if len(password) == 0:
            return render_template('auth/signup.html', error='Password cannot be empty')
        #if len(password) < 8:
        #    return render_template('auth/signup.html', error='Password must be at least 8 characters long')
        if password != confirm_password:
            return render_template('auth/signup.html', error='Passwords do not match')

        # create a new user if the email is not already in use
        user_query = User.objects.raw({ 'email': email })
        if user_query.count() != 0:
            return render_template('auth/signup.html', error='Email already in use')

        user = User(
            email=email,
            password_hash=generate_password_hash(password)
        ).save()

        return render_template('auth/signupsuccess.html')

@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    if 'auth' in session:
        session['auth'] = {
            'isAuthenticated': False,
            'user': {}
        }
    return render_template('auth/logoutsuccess.html')

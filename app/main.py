# ECE250 Testing Server
# For the Winter 2020 term.
# Author: John Liu

import os
from flask import (
    current_app as flask_app,
    render_template,
    g,
    url_for,
    session)
from app import db, auth, projects, users

"""Initialize server."""
# directory for where temporary files will be placed
flask_app.config['UPLOAD_DIR'] = os.path.expanduser('~')
db.init()

@flask_app.route('/')
def index():
    """Homepage."""
    return render_template('index.html')

"""/auth"""
flask_app.register_blueprint(auth.bp)

"""/projects"""
flask_app.register_blueprint(projects.bp)

"""/users"""
flask_app.register_blueprint(users.bp)

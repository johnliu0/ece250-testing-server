"""Entry point for the ECE250 testing server.

The Flask instance is initialized here and configured from the provided config
file. After initialization, the app.main module is imported and serves as the
root module for the server.

This module is only to ensure that the Flask app is properly initialized.

To start the server, use the start_dev.sh or the start_prod.sh script.
"""

from flask import Flask

flask_app = Flask(__name__)
flask_app.config.from_envvar('CFG_FILE')

with flask_app.app_context():
    import app.main

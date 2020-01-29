from flask import current_app as flask_app
from pymodm.connection import connect

def init():
    """Load MongoDB. Only needs to be called once at the start of the app."""
    connect(flask_app.config['MONGODB_URL'], alias='ece250ts')

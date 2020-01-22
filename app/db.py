from pymodm.connection import connect

def init():
    """Load MongoDB. Only needs to be called once at the start of the app."""
    connect('mongodb://localhost:27017/ece250testingserver', alias='ece250testingserver')

import os
import hashlib
import app.db
from pymodm import MongoModel, fields


class User(MongoModel):
    """
    User account.
    """
    email = fields.EmailField()
    password_hash = fields.CharField()

    class Meta:
        connection_alias = 'ece250testingserver'

def find_by_email(email):
    pass

def create_user(email, password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pw_hash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    print(pw_hash)



    return ''

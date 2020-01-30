from flask import (
    Blueprint,
    current_app as flask_app)
from models import user

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/', methods=['POST'])
def create_user():
    return 'facts'

@bp.route('/validate/<token>', methods=['GET'])
def validate_user(token):
    print(token)
    return 'validated!'

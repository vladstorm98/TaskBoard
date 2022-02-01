from flask import Blueprint

bp = Blueprint('desk', __name__, template_folder='templates')

from app.desk import routes

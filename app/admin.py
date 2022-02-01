from flask import Blueprint
from flask import render_template

from app import db


bp = Blueprint('admin', __name__, template_folder='templates')


@bp.route('/t')
def login():
    return render_template('admin.html')

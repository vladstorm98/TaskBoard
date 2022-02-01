from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime)
    profile = db.relationship('Profile', backref='user', lazy='dynamic')


class Profile(db.Model):
    __tablename__ = 'profile'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    number = db.Column(db.Integer)
    price = db.Column(db.String(32))
    address = db.Column(db.String(128), index=True)
    about_client = db.Column(db.String(256))
    last_order = db.Column(db.String(32))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tasks = db.relationship('Task', backref='client', lazy='dynamic')


class Task(db.Model):
    __tablename__ = 'task'
    __searchable__ = ['title', 'address', 'note', 'price']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32))
    name = db.Column(db.String(128))
    address = db.Column(db.String(128))
    note = db.Column(db.String(512))
    price = db.Column(db.String(32))
    date = db.Column(db.String(32))
    in_progress = db.Column(db.Boolean)
    client_id = db.Column(db.Integer, db.ForeignKey('profile.id'))

db.create_all()
db.session.commit()

# from flask import Flask
# from flask_babel import Babel
# from flask_babel import format_datetime
# from datetime import datetime
# from flask import render_template
#
# ap = Flask(__name__)
# babel = Babel(ap)
#
# @ap.route('/', methods=['GET'])
# def index():
#     f = format_datetime(datetime(1987, 3, 5, 17, 12), 'EEEE, d. MMMM yyyy H:mm')
#
#     print(f)
#     return render_template('1')
#
#
# ap.run()

import jwt
from time import time
from hashlib import md5  # для аватара
from flask import flash
from flask_babel import _

from app import db


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

    @classmethod
    def create_client(cls, first_name, last_name, number, price, address,
                      about_client):
        try:
            client = cls(first_name=first_name.title(),
                         last_name=last_name.title(),
                         number=number, price=price, address=address,
                         about_client=about_client)
            db.session.add(client)
            db.session.commit()
            flash(_('The profile was successfully created'), 'success')
            return True

        except:
            flash(_('An error occurred while creating a record.'), 'error')
            return False

    def avatar(self, size):
        """ Return avatar-image from Gravatar """
        digest = self.id
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    @classmethod
    def update_last_order(cls, client_id, date):
        try:
            client = cls.query.filter(cls.id == client_id).first()
            client.last_order = date
            db.session.commit()
            return True

        except:
            flash(_('An error occurred while changing the last order date'),
                  'error')
        return False

    @classmethod
    def delete_profile(cls, id):
        try:
            db.session.query(cls).filter_by(id=id).delete()
            db.session.commit()
            flash(_('The profile was successfully deleted'), 'success')
            return True

        except:
            flash(_('An error occurred while deleting a profile.'), 'error')
            return False

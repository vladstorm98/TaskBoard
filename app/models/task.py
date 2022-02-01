from flask import flash
from flask_babel import _

from app import db
from app.models import SearchableMixin


class Task(SearchableMixin, db.Model):
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

    @classmethod
    def get_tasks(cls, in_progress=True):
        try:
            if in_progress:
                tasks = cls.query.filter_by(in_progress=True).all()
            else:
                tasks = cls.query.filter_by(in_progress=False).all()
            return tasks

        except:
            flash(_('An error occurred while retrieving records.'), 'error')
        return ''

    @classmethod
    def create_task(cls, title, address, note, price, date,
                    client_id=None, name=None):
        try:
            task = cls(title=title, address=address, note=note, price=price,
                       date=date, client_id=client_id, name=name,
                       in_progress=True)
            db.session.add(task)
            db.session.commit()
            flash(_('The record was successfully created'), 'success')
            return True

        except:
            flash(_('An error occurred while creating a record.'), 'error')
            return False

    @classmethod
    def delete_task(cls, id):
        try:
            db.session.query(cls).filter_by(id=id).delete()
            db.session.commit()
            flash(_('The record was successfully deleted'), 'success')
            return True

        except:
            flash(_('An error occurred while deleting a record.'), 'error')
            return False

    @classmethod
    def transfer_task(cls, id):
        try:
            task = cls.query.filter(cls.id == id).first()
            if task.in_progress == False:
                task.in_progress = True
            else:
                task.in_progress = False
            db.session.commit()

            flash(_('The record has been transferred to the archive'), 'success')
            return True

        except:
            flash(_('An error occurred while transferring a recording to '
                    'the archive'), 'error')
            return False


# python manage.py db init
# python manage.py db migrate -m "initial migration"
# python manage.py db upgrade

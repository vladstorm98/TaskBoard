from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import IntegerField
from wtforms import SubmitField
from wtforms import SelectField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import NumberRange
from wtforms.validators import Length
from flask_babel import lazy_gettext as _l

from app.models.profile import Profile
from app import db

title = [_l('Support'), _l('General')]
years = [2021, 2022]
months = [(1, _l('January')), (2, _l('February')), (3, _l('March')),
          (4, _l('April')), (5, _l('May')), (6, _l('June')),
          (7, _l('July')), (8, _l('August')), (9, _l('September')),
          (10, _l('October')), (11, _l('November')), (12, _l('December'))]


class TaskForm(FlaskForm):
    title = SelectField(_l('Type of work:'), choices=title)
    address = StringField(_l('Address:'), validators=[DataRequired(),
                                                      Length(max=128)])
    note = TextAreaField(_l('Note:'), validators=[Length(max=512)])
    price = StringField(_l('Price:'), validators=[DataRequired(),
                                                  Length(max=32)])
    time = StringField(_l('Time:'), validators=[DataRequired()])
    day = IntegerField(_l('Day:'), validators=[DataRequired(),
                                               NumberRange(min=1, max=31)])
    month = SelectField(_l('Month:'), choices=months)
    year = SelectField(_l('Year:'), choices=years)
    submit = SubmitField(_l('Add'))


class ClientTaskForm(FlaskForm):
    title = SelectField(_l('Type of work:'), choices=title)
    client = SelectField(_l('Client:'), choices=[])
    note = TextAreaField(_l('Addition:'), validators=[Length(max=512)])
    time = StringField(_l('Time:'), validators=[DataRequired()])
    day = IntegerField(_l('Day:'), validators=[NumberRange(min=1, max=31)])
    month = SelectField(_l('Month:'), choices=months)
    year = SelectField(_l('Year:'), choices=years)
    submit = SubmitField(_l('Add'))

    def set_choices(self):
        self.client.choices = [(client.id,
                                client.first_name + ' ' + client.last_name)
                               for client in db.session.query(Profile).all()]


class CalendarForm(FlaskForm):
    month = SelectField(_l('Month:'), choices=months)
    year = SelectField(_l('Year:'), choices=years)
    submit = SubmitField(_l('Set'))


class SearchForm(FlaskForm):
    q = StringField(_l('What to search?'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)

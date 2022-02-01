from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import SubmitField
from wtforms import SelectField
from wtforms import IntegerField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Optional
from wtforms.validators import Length
from flask_babel import lazy_gettext as _l


class ClientForm(FlaskForm):
    first_name = StringField(_l('First name'), validators=[DataRequired()])
    last_name = StringField(_l('Last name'), validators=[DataRequired()])
    number = IntegerField(_l('Phone number:'), validators=[Optional()])
    price = StringField(_l('Price:'),
                        validators=[DataRequired(), Length(max=32)])
    address = StringField(_l('Address:'),
                          validators=[DataRequired(), Length(max=128)])
    about_client = TextAreaField(_l('About client:'),
                                 validators=[Length(max=512)])
    submit = SubmitField(_l('Add'))

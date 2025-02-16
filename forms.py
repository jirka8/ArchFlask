from openpyxl.drawing.text import TextField
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import TextAreaField, SubmitField


class AreasForm(FlaskForm):
    title = StringField('Nazev lokality', validators=[validators.DataRequired()])
    decription = TextAreaField('Popis lokality', validators=[validators.DataRequired()])
    submit = SubmitField('Ulozit')

class DatingForm(FlaskForm):
    title = StringField('Nazev datace', validators=[validators.DataRequired()])
    parent_id = SelectField('Nadrazena kategorie', coerce=int, validate_choice=False)
    submit = SubmitField('Ulozit')

from openpyxl.drawing.text import TextField
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from wtforms.fields.choices import SelectField, SelectMultipleField
from wtforms.fields.datetime import DateTimeField, DateTimeLocalField
from wtforms.fields.simple import TextAreaField, SubmitField, MultipleFileField


class AreasForm(FlaskForm):
    title = StringField('Nazev lokality', validators=[validators.DataRequired()])
    description = TextAreaField('Popis lokality', validators=[validators.DataRequired()])
    submit = SubmitField('Ulozit')

class DatingForm(FlaskForm):
    title = StringField('Nazev datace', validators=[validators.DataRequired()])
    parent_id = SelectField('Nadrazena kategorie', coerce=int, validate_choice=False)
    submit = SubmitField('Ulozit')

class CategoryForm(FlaskForm):
    title = StringField('Nazev kategorie', validators=[validators.DataRequired()])
    parent_id = SelectField('Nadrazena kategorie', coerce=int, validate_choice=False)
    submit = SubmitField('Ulozit')

class ItemsForm(FlaskForm):
    title = StringField('Nazev nálezu', validators=[validators.DataRequired()])
    description = TextAreaField('Popis nálezu', validators=[validators.DataRequired()])
    found_at = DateTimeLocalField('Datum a čas nálezu', format='%m. %d. %Y')
    location = StringField('GPS souřadnice')
    area_id = SelectField('Lokalita', coerce=int, validate_choice=False)
    categories = SelectMultipleField('Kategorie', coerce=int, validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Pouze obrázky!')])
    dating = SelectMultipleField('Datace', coerce=int)
    images = MultipleFileField('Fotografie')
    submit = SubmitField('Ulozit')
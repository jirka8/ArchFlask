from database import db_session
from flask import request
from sqlalchemy import or_, and_
from models import *
from forms import *

# input data for form parent select
def select_parents(model, item_id = 0):
    p = [(0, 'Nema nadrazenou kategorii')]
    if model == 'dating':
        dating = Dating.query.filter(
            or_(
                Dating.parent_id == 0,
                Dating.parent_id == None
            )
        ).all()
        for d in dating:
            p.extend(Dating.select_choices(d, item_id))
    if model == 'categories':
        categories = Categories.query.filter(
            or_(
                Categories.parent_id == 0,
                Categories.parent_id == None
            )
        ).all()
        for c in categories:
            p.extend(Categories.select_choices(c, item_id))
    return p

def prepare_item_form():
    form = ItemsForm(request.form)
    categories = Categories.query.filter(Categories.parent_id == None).all()
    datings = Dating.query.filter(Dating.parent_id == None).all()
    areas = Areas.query.all()

    cat_choices = []
    dat_choices = []
    areas_choices = [(0, 'Nemá nastavenou lokalitu')]

    for c in categories:
        cat_choices.extend(c.select_choices())

    for d in datings:
        dat_choices.extend(d.select_choices())

    for a in areas:
        areas_choices.extend([(a.id, a.title)])

    form.categories.choices = cat_choices
    form.dating.choices = dat_choices
    form.area_id.choices = areas_choices

    return form
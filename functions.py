from flask import request
from sqlalchemy import or_, and_, insert, update, delete
from database import db_session
from models import *
from forms import *
import os
from werkzeug.utils import secure_filename

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

# prepare categories and dating data to item form
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

# save items categories relations
def save_item_categories(categories, item_id):
    # delete data (in case of updating)
    db_session.execute(delete(items_categories).where(items_categories.c.item_id == item_id))
    db_session.commit()
    # insert data
    for c in categories:
        db_session.execute(insert(items_categories).values(item_id=item_id, category_id=c))
        db_session.commit()

# save items dating relations
def save_item_dating(dating, item_id):
    # delete data (in case of updating)
    db_session.execute(delete(items_dating).where(items_dating.c.item_id == item_id))
    db_session.commit()
    # insert data
    for d in dating:
        db_session.execute(insert(items_dating).values(item_id=item_id, dating_id=d))
        db_session.commit()

# save items images
def save_item_images(images, item_id):
    save_path = f'{os.getcwd()}/photos'
    for image in images.getlist('images'):
        if image.filename != '':
            i = Images()
            i.file_name = f'{item_id}_{image.filename}'
            i.item_id = item_id

            filename = secure_filename(i.file_name)
            image.save(os.path.join(save_path, filename))

            db_session.add(i)
            db_session.commit()

# gps coordinates parser (to lat and lon str)
def parse_coordinates_from_input(coordinates):
    parts = [part.strip() for part in coordinates.split(',')]
    if len(parts) != 2:
        raise ValueError('Souřadnice musí být ve tvaru x,y!')
    return parts[0], parts[1]

# parse coordinates for db
def parse_coordinates(lat_str, lon_str):
    # latitude
    if lat_str.endswith('N'):
        latitude = float(lat_str[:-1])
    elif lat_str.endswith('S'):
        latitude = -float(lat_str[:-1])
    else:
        latitude = float(lat_str)

    # longitude
    if lon_str.endswith('E'):
        longitude = float(lon_str[:-1])
    elif lon_str.endswith('W'):
        longitude = -float(lon_str[:-1])
    else:
        longitude = float(lon_str)

    return latitude, longitude
from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2.shape import to_shape
from markupsafe import Markup
import folium

from database import db_session, DB_URL
from sqlalchemy import or_, and_, insert, update, delete
from models import Areas, Dating, Categories, Items
from forms import *
from flask_wtf import CSRFProtect
from functions import *

# app configuration
app = Flask(__name__)
app.config["SECRET_KEY"] = "abracadabra"
app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'united'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
db = SQLAlchemy(app)
csrf = CSRFProtect(app)

# bootstrap
bootstrap = Bootstrap5(app)

# routes
@app.route('/')
def index():
    return render_template('index.html')

# templates filters
@app.template_filter('render_map')
def render_map(map_obj):
    return Markup(map_obj._repr_html_())

# routes items
@app.route('/items')
def items():
    page = request.args.get('page', 1, type=int)
    query = db.session.query(Items).order_by(Items.found_at.desc())
    items = db.paginate(query, page=page, per_page=10)
    return render_template('items.html', items=items)
@app.route('/items/<item_id>')
def view_item(item_id):
    item = Items.query.get(item_id)
    #print(parse_coordinates_to_readable(to_shape(item.location)))
    point = to_shape(item.location)
    lon = point.x
    lat = point.y

    m = folium.Map(location=[lat, lon], zoom_start=15)

    folium.Marker(
        location=[lat, lon],
        popup=f"<b>{item.title}</b>",
        tooltip=item.title
    ).add_to(m)

    return render_template('view_item.html', item=item, map=m)
@app.route('/items/add', methods=['GET', 'POST'])
def add_item():
    # prepare and fill form
    form = prepare_item_form()

    if request.method == 'POST' and form.validate():
        try:
            # set and save model
            item = Items()
            item.title = form.title.data
            item.description = form.description.data
            if form.location.data:
                # process lat,lon
                lat_str, lon_str = parse_coordinates_from_input(form.location.data)
                lat, lon = parse_coordinates(lat_str, lon_str)
                wkt_point = f'POINT({lon} {lat})'
                item.location = wkt_point
            item.found_at = form.found_at.data
            item.area_id = form.area_id.data if form.area_id.data != 0 else None
            db_session.add(item)
            db_session.commit()
            # save categories and etc.
            save_item_categories(form.categories.data, item.id)
            save_item_dating(form.dating.data, item.id)
            save_item_images(request.files, item.id)
            # flash message and redirect
            flash('Nález byl úspěšně uložený.', 'success')
            return redirect(url_for('items'))
        except Exception as e:
            db.session.rollback()
            flash(f'Při ukládání se vyskytly následující chyby: {str(e)}', 'error')

    return render_template('add_item.html', form=form)
@app.route('/items/edit/<item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    return render_template('edit_item.html')
@app.route('/items/delete/<item_id>', methods=['GET', 'POST'])
def delete_item(item_id):
    return True

#routes areas
@app.route('/areas')
def areas():
    areas = Areas.query.order_by(Areas.created.desc()).all()
    return render_template('areas.html', areas=areas)
@app.route('/areas/add', methods=['GET', 'POST'])
def add_area():
    form = AreasForm(request.form)
    if request.method == 'POST' and form.validate():
        a = Areas(form.title.data, form.description.data)
        db_session.add(a)
        db_session.commit()
        flash('Lokalita byla uspesne pridana.', 'success')
        return redirect(url_for('areas'))
    return render_template('add_area.html', form=form)
@app.route('/areas/edit/<area_id>', methods=['GET', 'POST'])
def edit_area(area_id):
    area = Areas.query.get(area_id)

    if area:
        form = AreasForm(request.form)

        if request.method == 'POST' and form.validate():
            area.title = form.title.data
            area.description = form.description.data
            db_session.add(area)
            db_session.commit()
            flash('Lokalita byla uspesne upravena.', 'success')
            return redirect(url_for('areas'))

        form.title.data = area.title
        form.description.data = area.description
        return render_template('edit_area.html', form=form)
    else:
        flash('Lokalita nenalezena!', 'error')
        return redirect(url_for('areas'))
@app.route('/areas/delete/<area_id>', methods=['GET', 'POST'])
def delete_area(area_id):
    area = Areas.query.get(area_id)
    if area:
        db_session.delete(area)
        db_session.commit()
        flash('Lokalita byla uspesne smazana.', 'success')
        return redirect(url_for('areas'))
    else:
        flash('Lokalita nenalezena!', 'error')
        return redirect(url_for('areas'))

#routes dating
@app.route('/dating')
def dating():
    dating = Dating.query.filter(or_(Dating.parent_id == 0, Dating.parent_id == None)).all()
    return render_template('dating.html', dating=dating)
@app.route('/dating/add', defaults={'parent_id': None}, methods=['GET', 'POST'])
@app.route('/dating/add/<parent_id>', methods=['GET', 'POST'])
def add_dating(parent_id):
    form = DatingForm(request.form, parent_id=parent_id)
    parents = select_parents('dating')
    form.parent_id.choices = parents

    if request.method == 'POST' and form.validate():
        d = Dating(form.parent_id.data if form.parent_id.data != 0 else None, form.title.data)
        db_session.add(d)
        db_session.commit()
        flash('Datace byla uspesne pridana.', 'success')
        return redirect(url_for('dating'))
    return render_template('add_dating.html', dating=dating, form=form)
@app.route('/dating/edit/<dating_id>', methods=['GET', 'POST'])
def edit_dating(dating_id):
    dating = Dating.query.get(dating_id)
    if dating:
        form = DatingForm(request.form)
        parents = select_parents('dating', dating_id)
        form.parent_id.choices = parents

        if request.method == 'POST' and form.validate():
            dating.title = form.title.data
            dating.parent_id = form.parent_id.data if form.parent_id.data != 0 else None
            db_session.add(dating)
            db_session.commit()
            flash('Datace byla uspesne upravena.', 'success')
            return redirect(url_for('dating'))

        form.title.data = dating.title
        form.parent_id.data = dating.parent_id

        return render_template('edit_dating.html', form=form)
    else:
        flash('Datace nenalezena!', 'error')
        return redirect(url_for('dating'))
@app.route('/dating/delete/<dating_id>', methods=['GET', 'POST'])
def delete_dating(dating_id):
    dating = Dating.query.get(dating_id)
    if dating:
        db_session.delete(dating)
        db_session.commit()
        flash('Datace byla uspesne smazana.', 'success')
        return redirect(url_for('dating'))
    else:
        flash('Datace nenalezena!', 'error')
        return redirect(url_for('dating'))

#routes categories
@app.route('/categories')
def categories():
    categories = Categories.query.filter(Categories.parent_id == None).all()
    return render_template('categories.html', categories=categories)
@app.route('/categories/add', defaults={'parent_id': None}, methods=['GET', 'POST'])
@app.route('/categories/add/<parent_id>', methods=['GET', 'POST'])
def add_category(parent_id):
    form = CategoryForm(request.form, parent_id=parent_id)
    parents = select_parents('categories')
    form.parent_id.choices = parents

    if request.method == 'POST' and form.validate():
        d = Categories(form.parent_id.data if form.parent_id.data != 0 else None, form.title.data)
        db_session.add(d)
        db_session.commit()
        flash('Kategorie byla uspesne pridana.', 'success')
        return redirect(url_for('categories'))
    return render_template('add_category.html', form=form)
@app.route('/categories/edit/<category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    category = Categories.query.get(category_id)
    if category:
        form = CategoryForm(request.form)
        parents = select_parents('categories', category_id)
        form.parent_id.choices = parents

        if request.method == 'POST' and form.validate():
            category.title = form.title.data
            category.parent_id = form.parent_id.data if form.parent_id.data != 0 else None
            db_session.add(category)
            db_session.commit()
            flash('Kategorie byla uspesne upravena.', 'success')
            return redirect(url_for('categories'))

        form.title.data = category.title
        form.parent_id.data = category.parent_id

        return render_template('edit_category.html', form=form)
    else:
        flash('Kategorie nenalezena!', 'error')
        return redirect(url_for('categories'))
@app.route('/categories/delete/<category_id>', methods=['GET', 'POST'])
def delete_category(category_id):
    category = Categories.query.get(category_id)
    if category:
        db_session.delete(category)
        db_session.commit()
        flash('Kategorie byla uspesne smazana.', 'success')
        return redirect(url_for('categories'))
    else:
        flash('Kategorie nenalezena!', 'error')
        return redirect(url_for('categories'))

@app.route('/photos/<image_id>')
def photos(image_id):
    image = Images.query.get(image_id)
    print(app.root_path + '/photos/' + image.file_name)
    return send_from_directory(app.root_path + '/photos/', image.file_name, conditional=True)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run(debug=True)
from random import choices
from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, request, flash, redirect, url_for
from database import db_session
from models import Areas, Dating
from forms import *
from flask_wtf import CSRFProtect

# app configuration
app = Flask(__name__)
app.config["SECRET_KEY"] = "abracadabra"
app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'united'

csrf = CSRFProtect(app)

# bootstrap
bootstrap = Bootstrap5(app)

def select_parents(model):
    p = [(0, 'Vyberte nadrazenou kategorii')]
    if model == 'dating':
        dating = Dating.query.filter(Dating.parent_id == 0).all()
        for d in dating:
            p.extend(Dating.select_choices(d))
    return p

# routes
@app.route('/')
def index():
    return render_template('index.html')

# routes items
@app.route('/items')
def items():
    return render_template('items.html')
@app.route('/items/add', methods=['GET', 'POST'])
def add_item():
    return render_template('add_item.html')
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
        a = Areas(form.title.data, form.decription.data)
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
            area.decription = form.decription.data
            db_session.add(area)
            db_session.commit()
            flash('Lokalita byla uspesne upravena.', 'success')
            return redirect(url_for('areas'))

        form.title.data = area.title
        form.decription.data = area.description
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
    dating = Dating.query.filter(Dating.parent_id == 0).all()
    return render_template('dating.html', dating=dating)
@app.route('/dating/add', methods=['GET', 'POST'])
def add_dating():
    form = DatingForm(request.form)
    parents = select_parents('dating')
    form.parent_id.choices = parents

    if request.method == 'POST' and form.validate():
        d = Dating(form.parent_id.data, form.title.data)
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
        parents = select_parents('dating')
        form.parent_id.choices = parents

        if request.method == 'POST' and form.validate():
            dating.title = form.title.data
            dating.parent_id = form.parent_id.data
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
    return True

#routes categories
@app.route('/categories')
def categories():
    return render_template('categories.html')
@app.route('/categories/add', methods=['GET', 'POST'])
def add_category():
    return render_template('add_category.html')
@app.route('/categories/edit/<category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    return render_template('edit_category.html')
@app.route('/categories/delete/<category_id>', methods=['GET', 'POST'])
def delete_category(category_id):
    return True

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run(debug=True)
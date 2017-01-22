#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, abort, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from logging import Formatter, FileHandler
from forms import *
import os

import string
import random

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from models import *
# Automatically tear down SQLAlchemy.

@app.teardown_request
def shutdown_session(exception=None):
    db.session.remove()


# Login required decorator.

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def home():
    return render_template('pages/placeholder.home.html')


def add_or_create_person(**kwargs):
    person = db.session.query(User).filter_by(**kwargs).first()
    if person:
        return (False, person)
    else:
        person = User(**kwargs)
        db.session.add(person)
        db.session.commit()
        return (True, person)


@app.route('/populate')
def populate():
    people = [
        {"name": "bob", "email": "bob@farming.com", "password": "chickens123"},
        {"name": "jane", "email": "jane@farming.com", "password": "wellyboots"},
        {"name": "casey", "email": "casey@barndoors.com", "password": "pinetrees"},
    ]

    new_count = 0
    existing_count = 0
    for person in people:
        new, person = add_or_create_person(**person)
        if new:
            new_count += 1
        else:
            existing_count += 1

    return "populated with " + str(new_count) + " new, " + str(existing_count) + " existing."


#NOTE: this page is intentionally unsecured so that a demonstrator can just check the passwords without looking inside the database manually.
@app.route('/userdetails')
def user_details():
    all_people = db.session.query(User).all()

    return render_template('pages/people.html', all_people = all_people)


@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    error_message = ""
    if request.method == 'POST':
        name = form['name'].data
        password = form['password'].data

        cookie_or_none = attempt_login(name, password)

        if cookie_or_none:
            resp = redirect(url_for('admin'))
            resp.set_cookie('auth', cookie_or_none)
            return resp
        else:
            error_message = "Failed to log in! Invalid username and/or password."

    print error_message
    return render_template('forms/login.html', form=form, error_message=error_message)


auth_tokens = {}

def attempt_login(name, password):
    sql = "select * FROM Users WHERE name='{name}' AND password='{password}'".format(name=name, password=password)
    result = db.engine.execute(sql)

    print bool(result)
    lines = 0
    for row in result:
        lines+=1

    print "lines", lines

    if lines:
        token = ''.join(random.choice(string.ascii_lowercase) for _ in range(10))

        global auth_tokens
        auth_tokens[token] = name

        return token


@app.route('/admin')
def admin():
    auth_token = request.cookies.get('auth')

    username = auth_tokens.get(auth_token)

    if username:
        return render_template('pages/admin.html', username=username)
    else:
        return "Error! you need to be logged in to view the admin panel."


@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)


@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)

# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)


# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

#!/usr/bin/env python
# coding: utf-8
from flask import Flask, render_template, redirect, url_for, request, flash
from flask import send_from_directory
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from os import path, listdir
from wtforms import Form, StringField, PasswordField, validators
from user import User, UserDoesntExist
import secret

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = '459169B62F4A6D64'
app.config['APPLICATION_ROOT'] = '/templates'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = u"You have to login first."
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return User.load(user_id)


@app.route('/')
def index():
    flag = ''
    if current_user.is_authenticated and current_user.username == 'admin':
        flag = secret.Flag
    return render_template('index.html', flag=flag)


class LoginForm(Form):
    username = StringField(u"Username", [validators.DataRequired()])
    password = PasswordField(u"Password", [validators.DataRequired()])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        try:
            user = User.login(form.username.data, form.password.data)
            login_user(user)

            return redirect(request.args.get('next') or url_for('index'))
        except UserDoesntExist:
            flash(u"Login failed.", 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


statics = path.join(path.abspath(path.dirname(__file__)), 'static')
for static in listdir(statics):
    def handler(filename, static=static):
        return send_from_directory(path.join(statics, static), filename)
    app.add_url_rule('/{}/<path:filename>'.format(static), static, handler)

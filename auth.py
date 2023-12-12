from flask import Blueprint, flash, redirect, url_for
from flask import render_template, request
from flask_login import login_user, login_required, logout_user

from werkzeug.security import check_password_hash

from .models import User


auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    # login code goes here
    remember = True

    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    print(username)
    print(password)
    print('from db:')
    if user:
        print(user.username)
        print(user.password)

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.index'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

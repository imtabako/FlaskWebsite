from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from datetime import datetime
from werkzeug.security import generate_password_hash

from . import db
from .models import Post, User


main = Blueprint('main', __name__)


# News funtionality
# Home page, show 3 top news
@main.route('/')
def index():
    posts = Post.query.order_by(Post.edited.desc()).limit(3)
    return render_template('index.html', posts=posts)


# Single news item
@main.route('/news/<int:id>')
def show_post(id):
    post = Post.query.get(id)

    if post is None:
        error = 'Новость не найдена'
        # flash(error)
        return render_template('post.html', error=error)

    return render_template('post.html', post=post)


# Show new news item editor, GET
@main.route('/news/create')
@login_required
def editor_post():
    return render_template('editor.html')


# Create new news item, POST
@main.route('/news/create', methods=['POST'])
@login_required
def create_post():
    title = request.form.get('title')
    body = request.form.get('body')

    error = None
    if not title:
        error = 'Необходим заголовк'
    elif not body:
        error = 'Новость не может быть пустой'

    if error is None:
        new_post = Post(author_username=current_user.username, editor_username=current_user.username, title=title, body=body)

        print(new_post)
        # add new post to database
        db.session.add(new_post)
        db.session.commit()
        print('added, commited')
        
        return redirect(url_for('main.show_post', id=new_post.id))

    flash(error)
    return redirect(url_for('main.index'))


# Show news item editor, GET
@main.route('/news/edit/<int:id>')
@login_required
def edit_post_show(id):
    post = Post.query.get(id)
    if post is None:
        error = 'Новость не найдена'
        return render_template('post.html', error=error)

    return render_template('editpost.html', post=post)


# Show news item editor, POST
@main.route('/news/edit/<int:id>', methods=['POST', 'PUT'])
@login_required
def edit_post(id):
    post = Post.query.get(id)
    if post is None:
        error = 'Новость не найдена'
        return render_template('post.html', error=error)

    title = request.form.get('title')
    body = request.form.get('body')
    editor = current_user.username
    edited = datetime.now()

    error = None
    if title is None:
        error = 'Необходим заголовок'
    if body is None:
        error = 'Новость не может быть пустой'

    print('editing post')
    print(post)
    
    post.title = title
    post.body = body
    post.editor = editor
    post.edited = edited

    db.session.commit()
    print('success')

    return redirect(url_for('main.index'))


# Delete news item
@main.route('/news/delete/<int:id>', methods=['POST', 'DELETE'])
@login_required
def delete_post():
    if current_user.id != 1:
        error = 'Недостаточно прав'
        return render_template('index.html')
    
    post = Post.query.get(id)
    print(post)


    if post is None:
        error = 'No such post'
        flash(error)
    else:
        db.session.delete(post)
        db.session.commit()

    return redirect(url_for('main.index'))


# User functionality
# Current user's profile
@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


# User's profile
@main.route('/user/<username>')
def show_profile(username):
    user = User.query.filter_by(username=username).first()
    print(user)
    if user:
        return render_template('profile.html', user=user)

    return render_template('profile.html', error='No such user')


# Admin functionality
# List of users (admin only)
@main.route('/users')
@login_required
def list_users():
    if current_user.id != 1:
        error = 'Недостаточно прав'
        return render_template('index.html')
    
    users = User.query.order_by(User.username).all()
    print(users)
    
    return render_template('userspanel.html', users=users)


# Create new user
@main.route('/users/create', methods=['POST'])
@login_required
def create_user():
    if current_user.id != 1:
        error = 'Недостаточно прав'
        return render_template('index.html')

    username = request.form.get('username')
    password = request.form.get('password')
    name = request.form.get('name')
    lastname = request.form.get('lastname')
    position = request.form.get('position')

    # validate
    error = None
    if not username:
        error = 'Необходим логин'
    elif not password:
        error = 'Необходим пароль'
    elif not name:
        error = 'Необходимо имя'
    elif not lastname:
        error = 'Необходима фамилия '

    print(username)
    print(password)
    print(name)
    print(lastname)
    print(position)

    if error is None:
        print(error)
        user = User.query.filter_by(username=username).first()
        print(user)
        print('got here')
        if user:
            error = 'Пользователь с таким логином уже существует'
            print(error)
            flash(error)
            return redirect(url_for('main.list_users'))
        
        new_user = User(username=username, password=generate_password_hash(password), name=name, lastname=lastname, position=position)
        # add new user to database
        db.session.add(new_user)
        db.session.commit()
        print('added, commited')

    flash(error)

    return redirect(url_for('main.list_users'))
  

# Edit existing user
@main.route('/users/edit/<int:id>', methods=['POST', 'PUT'])
@login_required
def edit_user(id):
    if current_user.id != 1:
        error = 'Недостаточно прав'
        flash(error)
        abort(401)
        return render_template('index.html')

    username = request.form.get('username')
    password = request.form.get('password')
    name = request.form.get('name')
    lastname = request.form.get('lastname')
    position = request.form.get('position')

    user = User.query.get(id)
    print('editing')
    print(user)

    if user is None:
        error = 'No such user'
        flash(error)
        return redirect(url_for('main.list_users'))
    
    user.username = username
    if password is not None:
        user.password = generate_password_hash(password)
    user.name = name
    user.lastname = lastname
    user.position = position

    db.session.commit()
    print('success')

    return redirect(url_for('main.list_users'))


# Delete existing user
@main.route('/users/delete/<int:id>', methods=['POST', 'DELETE'])
@login_required
def delete_user(id):
    print('deleting ', id)
    if current_user.id != 1:
        error = 'Недостаточно прав'
        return render_template('index.html')
    
    user = User.query.get(id)
    print(user)
    

    if user is None:
        error = 'No such user'
        flash(error)
        return redirect(url_for('main.list_users'))
    
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('main.list_users'))

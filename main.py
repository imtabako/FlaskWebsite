from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import errno
import os
import time
from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for, request
from flask_login import current_user, login_required
from datetime import datetime
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

import email_validator

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_uploads import UploadSet, IMAGES
from wtforms import BooleanField, MultipleFileField, RadioField, SelectField, StringField, SubmitField, TextAreaField, ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp

import imaplib
from smtplib import SMTP_SSL, SMTP_SSL_PORT


from . import db
from .models import Post, User


main = Blueprint('main', __name__)


SMTP_HOST = "smtp.yandex.ru"
SMTP_USER = ""
SMTP_PASSWORD = ""

NEWS_TITLE_MAXLEN = 100

UPLOAD_FOLDER = 'user_uploads/'
UPLOAD_FOLDER_FULL = '/static/user_uploads/'
images = UploadSet('images', IMAGES)


# WTForm for news creation/editing
class PostForm(FlaskForm):
    title = StringField('Заголовок новости:',
                         validators=[DataRequired(), Length(max=NEWS_TITLE_MAXLEN)],
                         render_kw={"placeholder": "Введите заголовок"})
    body = TextAreaField('Напишите новостную статью:', validators=[DataRequired()])
    main_image = FileField('Главное изображение', validators=[FileAllowed(images)])


# WTForm for feedback
class FeedbackForm(FlaskForm):
    def validate_full_name(form, field):
        words = field.data.split()
        if len(words) < 3:
            raise ValidationError('Введите имя фамилию и отчество')

    organization = StringField(
        'Наименование организации:',
        validators=[DataRequired()],
        render_kw={"placeholder": "Наименование организации"})
    inn = StringField(
        'ИНН:',
        validators=[DataRequired(), Length(min=10, max=10, message='ИНН состоит из 10 цифр'), Regexp("^\d+$")],
        render_kw={"placeholder": "ИНН"})
    rad = RadioField(
        'Тип контрагента:',
        validators=[DataRequired()],
        choices=[('option1', 'Юридическое лицо'), ('option2', 'Госучреждения'), ('option3', 'Индивидуальный предприниматель')])
    kpp = StringField(
        'КПП:',
        validators=[DataRequired(), Length(min=9, max=9, message='КПП состоит из 9 цифр'), Regexp("^\d+$")],
        render_kw={"placeholder": "КПП"})
    name = StringField(
        'ФИО:',
        validators=[DataRequired(), Regexp('^(?:[A-Za-zА-Яа-я\']+\s){2}[A-Za-zА-Яа-я\']+$')],
        render_kw={"placeholder": "ФИО"})
    phone = StringField(
        'Телефон:',
        validators=[DataRequired(), Regexp('^\+7 \(9\d{2}\) \d{3}-\d{2}\d{2}$', message='Неверный формат телефона')],
        render_kw={"placeholder": "+7(555)555-5555"})
    email = StringField(
        'Адрес электронной почты:',
        validators=[DataRequired(), Email(message='Неверный формат почты')],
        render_kw={"placeholder": "Адрес электронной почты"})
    preference = SelectField(
        'Предпочтительный способ коммуникации:',
        choices=[('tel', 'Телефон'), ('email', 'Электроная почта')],
        validators=[DataRequired()],
        render_kw={"placeholder": "Предпочтительный способ коммуникации"})
    information = StringField(
        'Информация:',
        validators=[DataRequired()],
        render_kw={"placeholder": "Информация"})
    docs = MultipleFileField(
        'Выберите файл(ы):',
        validators=[FileRequired('Выберите хотя бы один файл'), FileAllowed([])])
    agreement = BooleanField(
        'Я даю согласие на обработку моих персональных данных', 
        validators=[DataRequired()])
    submit = SubmitField('Отправить')


# functions for uploading images and storing them
@main.route('/upload_image', methods=['POST'])
def upload_image():
    if 'image' in request.files:
        image = request.files('image')
        filename = secure_filename(image.filename).lower()
        basename, image_ext = os.path.splitext(filename)

        current_time = int(time.time() * 1000)
        timestr = time.strftime("%y%m%d") + current_time

        filename = secure_filename(basename + "-" + timestr + image_ext)
        img_path = os.path.join(UPLOAD_FOLDER_FULL, filename)

        print(filename)
        print(img_path)

        if not os.path.exists(UPLOAD_FOLDER_FULL):
            print('no folder')
            try:
                os.makedirs(UPLOAD_FOLDER_FULL)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

        image.save(img_path)
        location = url_for('static', filename=UPLOAD_FOLDER + filename)
        print(location)

        return jsonify({'success': True, 'location': location})
    return jsonify({'success': False, 'error': 'Не предоставлен файл'})


@main.route('/about')
def about_page():
    print(images)
    return render_template('about.html')


@main.route('/feedback', methods=['GET', 'POST'])
def feedback():
    form = FeedbackForm(meta={'locales': ['ru_RU', 'ru']})

    print(request.method)
    print(form)

    print(form.organization.data)
    print(form.inn.data)
    print(form.rad.data)
    print(form.kpp.data)
    print(form.name.data)
    print(form.phone.data)
    print(form.email.data)
    print(form.inn.data)


    if form.validate_on_submit():
        print('success')

        # send email
        from_email = SMTP_USER
        to_emails = [SMTP_USER]

        # Create text and HTML bodies for email
        body = '\n'.join([
            "Организация: " + form.organization.data,
            "ИНН: " + form.inn.data,
            "Тип контрагента: " + form.rad.data,
            "КПП: " + form.kpp.data,
            "ФИО: " + form.name.data,
            "Электронная почта: " + form.email.data,
            "Телефон: " + form.phone.data,
            "Предпочтительный способ коммуникации: " + form.preference.data,
            "Информация: " + form.information.data,
        ])
        print(body)

        email_message = MIMEMultipart()
        email_message.add_header('To', ', '.join(to_emails))
        email_message.add_header('From', from_email)
        email_message.add_header('Subject', 'Обратная связь')
        email_message.add_header('X-Priority', '1')  # Urgent/High priority
        text_part = MIMEText(body, 'plain')
        # email_message.set_content(body)

        email_message.attach(text_part)


        # connect, authenticate, and send mail
        smtp_server = SMTP_SSL(SMTP_HOST, port=SMTP_SSL_PORT)
        smtp_server.set_debuglevel(1)  # Show SMTP server interactions
        smtp_server.login(SMTP_USER, SMTP_PASSWORD)
        smtp_server.sendmail(from_email, to_emails, email_message.as_bytes())
        # disconnect
        smtp_server.quit()

    return render_template('feedback.html', form=form)


# News funtionality
# Home page, show 3 top news
@main.route('/')
def index():
    posts = Post.query.order_by(Post.edited.desc()).limit(3)
    return render_template('index.html', posts=posts, post=posts[0])


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
@main.route('/news/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()

    if form.validate_on_submit():
        new_post = Post(author_username=current_user.username, editor_username=current_user.username, title=form.title.data, body=form.body.data)

        print(new_post)
        # add new post to database
        db.session.add(new_post)
        db.session.commit()
        print('added, commited')

        return redirect(url_for('main.show_post', id=new_post.id))

    print('not validated')
    return render_template('createpost.html', form=form)


# Create new news item, POST
@main.route('/news/create2', methods=['POST'])
@login_required
def create_post2():
    title = request.form.get('title')
    body = request.form.get('body')

    if 'file' not in request.files:
        print('No file part')
        # error='Необходимо добавить фото'
        
        # return redirect(url_for('main.create_post'))
    
    print(title)
    print(body)
    print(request.files)

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

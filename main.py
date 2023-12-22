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

from smtplib import SMTP_SSL, SMTP_SSL_PORT


from . import db
from .models import Post, User

from website import SMTP_HOST, SMTP_USER, SMTP_PASSWORD


main = Blueprint('main', __name__)

NEWS_TITLE_MAXLEN = 100

UPLOAD_FOLDER = 'user_uploads/'
UPLOAD_FOLDER_FULL = './website/static/user_uploads/'
images = UploadSet('images', IMAGES)


# WTForm for news creation/editing
class PostForm(FlaskForm):
    title = StringField('Заголовок новости:',
                         validators=[DataRequired(), Length(max=NEWS_TITLE_MAXLEN)],
                         render_kw={"placeholder": "Введите заголовок"})
    body = TextAreaField('Напишите новостную статью:')
    submitBtn = SubmitField('Завершить')


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
        render_kw={
            "placeholder": "ИНН",
            "inputmode": "numeric",
            "pattern": "[0-9]{10}",
            "maxlength": "10",
            })
    rad = RadioField(
        'Тип контрагента:',
        validators=[DataRequired()],
        choices=[('option1', 'Юридическое лицо'), ('option2', 'Госучреждения'), ('option3', 'Индивидуальный предприниматель')])
    kpp = StringField(
        'КПП:',
        validators=[DataRequired(), Length(min=9, max=9, message='КПП состоит из 9 цифр'), Regexp("^\d+$")],
        render_kw={
            "placeholder": "КПП",
            "inputmode": "numeric",
            "pattern": "[0-9]{9}",
            "maxlength": "9"
            })
    name = StringField(
        'ФИО:',
        validators=[DataRequired(), Regexp('^(?:[A-Za-zА-Яа-я\']+\s){2}[A-Za-zА-Яа-я\']+$')],
        render_kw={"placeholder": "ФИО"})
    phone = StringField(
        'Телефон:',
        validators=[DataRequired(), Regexp('^\+7 \(\d{3}\) \d{3}-\d{4}$', message='Неверный формат телефона')],
        render_kw={"placeholder": "+7 (555) 555-5555"})
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
    # docs = MultipleFileField(
    #     'Выберите файл(ы):',
    #     validators=[FileRequired('Выберите хотя бы один файл'), FileAllowed(['jpg', 'jpeg', 'png', 'docs', 'pdf'], 'Только изображения, PDF-файлы и Word-файлы')])
    docs = MultipleFileField('Выберите файл(ы):')
    agreement = BooleanField(
        'Я даю согласие на обработку моих персональных данных', 
        validators=[DataRequired()])
    submit = SubmitField('Отправить')


@main.route('/success')
def success():
    return render_template('success.html')


@main.route('/test', methods=['GET', 'POST'])
@login_required
def test_tinymce():
    form = PostForm()
    if form.validate_on_submit():
        flash('Form submitted successfully', 'success')
        title = form.title.data
        body = form.body.data
        # print(title)
        # print(body)

        if len(body) == 0:
            flash('Новость не может быть пуста', 'error')
            return render_template('test_editor.html', form=form)
        return redirect(url_for('main.index'))
    
    # print('not validated')
    # print(form)
    return render_template('test_editor.html', form=form)


# functions for uploading images and storing them
@main.route('/upload_image', methods=['POST'])
def upload_image():
    # print('got here')
    # print(request.files)
    if 'file' in request.files:
        image = request.files.get('file')
        filename = secure_filename(image.filename).lower()
        basename, image_ext = os.path.splitext(filename)

        current_time = str(int(time.time() * 1000))
        timestr = time.strftime("%y%m%d") + current_time

        filename = secure_filename(basename + "-" + timestr + image_ext)
        img_path = os.path.join(UPLOAD_FOLDER_FULL, filename)

        # print(os.getcwd())
        # print(filename)
        # print(img_path)

        if not os.path.exists(UPLOAD_FOLDER_FULL):
            # print('no folder')
            try:
                os.makedirs(UPLOAD_FOLDER_FULL)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

        image.save(img_path)
        location = url_for('static', filename=UPLOAD_FOLDER + filename)
        # print(location)

        return jsonify({'success': True, 'location': location})
    return jsonify({'success': False, 'error': 'Не предоставлен файл'})


@main.route('/about')
def about_page():
    # print(images)
    return render_template('about.html')


@main.route('/feedback', methods=['GET', 'POST'])
def feedback():
    form = FeedbackForm(meta={'locales': ['ru_RU', 'ru']})

    # print(request.method)
    # print(form)

    # print(form.organization.data)
    # print(form.inn.data)
    # print(form.rad.data)
    # print(form.kpp.data)
    # print(form.name.data)
    # print(form.phone.data)
    # print(form.email.data)
    # print(form.inn.data)


    if form.validate_on_submit():
        # print('success')

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
        # print(body)

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


@main.route('/news')
def list_news():
    posts = Post.query.order_by(Post.edited.desc())
    return render_template('newslist.html', posts=posts)


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
        # print('Form submitted successfully')
        title = form.title.data
        body = form.body.data
        # print(title)
        # print([body, len(body)])

        if len(body) == 0:
            # print('empty body')
            # flash('Новость не может быть пустой', 'warning')
            return render_template('createpost.html', form=form)

        current_time = datetime.now()
        new_post = Post(
            author_username=current_user.username, editor_username=current_user.username, 
            created=current_time, edited=current_time,
            title=form.title.data, body=form.body.data)

        # print(new_post)
        # add new post to database
        db.session.add(new_post)
        db.session.commit()
        # print('added, commited')

        return redirect(url_for('main.show_post', id=new_post.id))

    # print('not validated')
    return render_template('createpost.html', form=form)


# Show news item editor, GET
@main.route('/news/edit/<int:id>')
@login_required
def edit_post_show(id):
    form = PostForm()

    post = Post.query.get(id)
    if post is None:
        error = 'Новость не найдена'
        return render_template('post.html', error=error)
    # title = post.title
    # body = post.body
    # editor = current_user.username
    # edited = datetime.now()

    return render_template('editpost.html', post=post, form=form)


# Show news item editor, POST
@main.route('/news/edit/<int:id>', methods=['POST', 'PUT'])
@login_required
def edit_post(id):
    form = PostForm()

    post = Post.query.get(id)
    if post is None:
        error = 'Новость не найдена'
        return render_template('post.html', error=error)
    title = post.title
    body = post.body
    editor = current_user.username
    edited = datetime.now()
    
    if form.validate_on_submit:
        title = form.title.data
        body = form.body.data
        editor = current_user.username
        edited = datetime.now()

        # print('editing post')
        # print(post)
    
        post.title = title
        post.body = body
        post.editor = editor
        post.edited = edited

        db.session.commit()
        # print('success')
        return redirect(url_for('main.index'))
    return render_template('editpost.html', post=post, form=form)


# Delete news item
@main.route('/news/delete/<int:id>', methods=['POST', 'DELETE'])
@login_required
def delete_post(id):
    if current_user.id != 1:
        error = 'Недостаточно прав'
        return render_template('index.html')
    
    post = Post.query.get(id)
    # print(post)

    if post is None:
        error = 'No such post'
        # flash(error)
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
    # print(user)
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
    # print(users)
    
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

    # print(username)
    # print(password)
    # print(name)
    # print(lastname)
    # print(position)

    if error is None:
        # print(error)
        user = User.query.filter_by(username=username).first()
        # print(user)
        # print('got here')
        if user:
            error = 'Пользователь с таким логином уже существует'
            # print(error)
            # flash(error)
            return redirect(url_for('main.list_users'))
        
        new_user = User(username=username, password=generate_password_hash(password), name=name, lastname=lastname, position=position)
        # add new user to database
        db.session.add(new_user)
        db.session.commit()
        # print('added, commited')

    # flash(error)

    return redirect(url_for('main.list_users'))
  

# Edit existing user
@main.route('/users/edit/<int:id>', methods=['POST', 'PUT'])
@login_required
def edit_user(id):
    if current_user.id != 1:
        error = 'Недостаточно прав'
        # flash(error)
        abort(401)
        return render_template('index.html')

    username = request.form.get('username')
    password = request.form.get('password')
    name = request.form.get('name')
    lastname = request.form.get('lastname')
    position = request.form.get('position')

    user = User.query.get(id)
    # print('editing')
    # print(user)

    if user is None:
        error = 'No such user'
        # flash(error)
        return redirect(url_for('main.list_users'))
    
    user.username = username
    if password is not None:
        user.password = generate_password_hash(password)
    user.name = name
    user.lastname = lastname
    user.position = position

    db.session.commit()
    # print('success')

    return redirect(url_for('main.list_users'))


# Delete existing user
@main.route('/users/delete/<int:id>', methods=['POST', 'DELETE'])
@login_required
def delete_user(id):
    # print('deleting ', id)
    if current_user.id != 1:
        error = 'Недостаточно прав'
        return render_template('index.html')
    
    user = User.query.get(id)
    # print(user)

    if user is None:
        error = 'No such user'
        # flash(error)
        return redirect(url_for('main.list_users'))
    
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('main.list_users'))

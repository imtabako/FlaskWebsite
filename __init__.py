import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import generate_password_hash

# IMAP_IN_PORT = 993
# EMAIL_HOST_IN_ADDR = "imap.yandex.ru"
# IMAP_OUT_PORT = 465
SMTP_HOST = "smtp.yandex.ru"
SMTP_USER = "mtpeshkin@yandex.ru"
SMTP_PASSWORD = "djxzrdzwxibqvumw"

UPLOAD_FOLDER = 'photos/'


# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        UPLOAD_FOLDER=UPLOAD_FOLDER,
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///db.sqlite'
    )
    db.init_app(app)

    # if test_config is None:
    #     # load the instance config, if it exists, when not testing
    #     app.config.from_pyfile('config.py', silent=True)
    # else:
    #     # load the test config if passed in
    #     app.config.from_mapping(test_config)

    # # ensure the instance folder exists
    # try:
    #     os.makedirs(app.instance_path)
    # except OSError:
    #     pass

    # # use database
    # from . import database
    # database.init_app(app)

    from . import models
    with app.app_context():
        db.create_all()

    # try to create admin and 2 sample news if no users (first run)
    from .models import User, Post
    with app.app_context():
        if not User.query.all():
            print('Creating admin, 2 posts')

            admin = User(username='admin', password=generate_password_hash('admin'), name='Admin', lastname='Admin', position='Admin')
            db.session.add(admin)

            post = Post(author_username='admin', editor_username='admin', title='Тестовый заголовок', body='Текст текст текст текст текст', author_id=admin.id)
            db.session.add(post)
            post = Post(author_username='admin', editor_username='admin', title='Вторая новость', body='Длинные тексты (лонгриды), где большой объем сочетается с глубоким погружением в тему, становятся все более популярными в печатных и онлайновых изданиях, так как позволяют изданию выделиться из информационного шума. Цели исследования – выявить распространенность лонгридов в российских СМИ и содержательные и композиционные особенности этих текстов. Исследование включает мониторинг публикаций в центральных российских изданиях и последующий контент-анализ 10 материалов из 10 печатных и онлайновых изданий. Выводы исследования: лонгриды присутствуют в изданиях разных типов: от ежедневных газет − до нишевых новостных сайтов. Они посвящены, как правило, описанию нового явления; имеют объем от 2 до 4 тыс. слов и построены по композиционной схеме чередования примеров и обобщений.\n\nКлючевые слова: лонгрид, жанры, тренд, российская пресса.', author_id=admin.id)
            db.session.add(post)
            db.session.commit()

    # user sessions handling
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # from .models import User 

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
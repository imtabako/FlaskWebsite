DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    lastname TEXT NOT NULL,
    position TEXT
);

CREATE TABLE post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_username TEXT NOT NULL,
    editor_username TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    edited TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    FOREIGN KEY (author_username) REFERENCES user (username)
);

INSERT INTO user (username, password, name, lastname, position) VALUES (
    'admin', 'pbkdf2:sha256:260000$itRm2ce1wtJfuuSv$6d46535d68c00cedc0b88e66d86dd80ffe3df8a5a7fc9704169a97db42de0908',
    'Администратор', 'Администратор', 'Администратор'
);

INSERT INTO post (author_username, editor_username, title, body) VALUES (
    'admin', 'admin', 'Тестовый заголовок', 'Текст текст текст текст текст текст текст текст текст текст текст текст текст'
);

INSERT INTO post (author_username, editor_username, title, body) VALUES (
    'admin', 'admin', 'Тестовый заголовок №2', 'Unlike the auth blueprint, the blog blueprint does not have a url_prefix. So the index view will be at /, the create view at /create, and so on. The blog is the main feature of Flaskr, so it makes sense that the blog index will be the main index.

However, the endpoint for the index view defined below will be blog.index. Some of the authentication views referred to a plain index endpoint. app.add_url_rule() associates the endpoint name ''index'' with the / url so that url_for(''index'') or url_for(''blog.index'') will both work, generating the same / URL either way.

In another application you might give the blog blueprint a url_prefix and define a separate index view in the application factory, similar to the hello view. Then the index and blog.index endpoints and URLs would be different.'
);
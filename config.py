# config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = "myrandomomdqwdqwkdnqw"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'users.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RECAPTCHA_PUBLIC_KEY = "6LdS6NsoAAAAAO7YoVRuJ4qVRZpd8-BxVNVkoWNq"
    RECAPTCHA_PRIVATE_KEY = "6LdS6NsoAAAAAAc0bV5RXMWougLtG4rGStVoCDob"
    RECAPTCHA_USE_SSL = False
    RECAPTCHA_OPTIONS = {'theme': 'black'}


config = {
    'default': Config
}

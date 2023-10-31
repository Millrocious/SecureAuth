import sqlalchemy as sa
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from loguru import logger

from config import config

db = SQLAlchemy()
moment = Moment()
SECRET_KEY = None
bcrypt = Bcrypt()
logger.add("out.log")
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config.get(config_name or 'default'))

    db.init_app(app)
    bcrypt.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)

    global SECRET_KEY
    SECRET_KEY = app.secret_key

    with app.app_context():
        from app.auth import auth_bp

        app.register_blueprint(auth_bp)

    engine = sa.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    inspector = sa.inspect(engine)
    if not inspector.has_table("users"):
        with app.app_context():
            db.drop_all()
            db.create_all()
            app.logger.info('create tables...')
            app.logger.info('Initialized the database!')

            from app.auth.models import User
            admin_user = User(username="Admin",
                              phone_number="+380988995701",
                              email="admin@email.com",
                              password="admin_user")
            admin_user.is_admin = True
            db.session.add(admin_user)
            db.session.commit()
    else:
        app.logger.info('Database already contains the users table.')

    return app
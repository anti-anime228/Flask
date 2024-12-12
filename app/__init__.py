from flask import Flask
from flask_login import LoginManager
from .ext import db

login_manager = LoginManager()
login_manager.login_view = 'main.login'

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
    app.config['SECRET_KEY'] = 'your_secret_key'

    db.init_app(app)
    login_manager.init_app(app)



    with app.app_context():
        db.create_all()

    from . import auth
    from . import routers
    routers.init_app(app)

    return app

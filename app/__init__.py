from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.secret_key = "supersecretkey123"
    app.debug = True

    # Database config
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///events.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    Bootstrap(app)

    login_manager.init_app(app)
    login_manager.login_view = '/Log_In' # Define the view function for login

    from .views import mainbp
    app.register_blueprint(mainbp)

    return app

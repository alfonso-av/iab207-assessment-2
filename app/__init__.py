from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.secret_key = "supersecretkey123"
    app.debug = True

    # Database config
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///events.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    Bootstrap(app)

    from .views import mainbp
    app.register_blueprint(mainbp)

    return app

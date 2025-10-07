from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # we use this utility module to display forms quickly
    Bootstrap(app)

    # A secret key for the session object
    app.secret_key = 'somerandomvalue'

    # Configure and initialise DB
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'  # Changed from site.db
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    db.init_app(app)
    
    # Create database tables
    with app.app_context():
        # Import models to ensure they're registered with SQLAlchemy
        from . import models
        db.create_all()
    
    # add Blueprints
    from . import views
    app.register_blueprint(views.mainbp)
    from . import events
    app.register_blueprint(events.eventbp)
  
    
   

    return app
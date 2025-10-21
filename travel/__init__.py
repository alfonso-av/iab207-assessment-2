from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
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


    #add login manager support
    #initialize the login manager
    login_manager = LoginManager()
    
    #set the name of the login function that lets user login
    # in our case it is auth.login (blueprintname.viewfunction name)
    login_manager.login_view='auth.login'
    login_manager.init_app(app)

    #create a user loader function takes userid and returns User
    from .models import User  # importing here to avoid circular references
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    

    #add login manager support
    #initialize the login manager
    login_manager = LoginManager()
    
    #set the name of the login function that lets user login
    # in our case it is auth.login (blueprintname.viewfunction name)
    login_manager.login_view='auth.login'
    login_manager.init_app(app)

    #create a user loader function takes userid and returns User
    from .models import User  # importing here to avoid circular references
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
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
    app.register_blueprint(events.destbp)
    from . import auth
    app.register_blueprint(auth.authbp)
    
    # Register the new bookings blueprint
    from .bookings import bookingsbp
    app.register_blueprint(bookings.bookingsbp)

    # Create database tables
    with app.app_context():
        # Explicitly import all models to ensure the new 'Booking' table is created
        from .models import User, Event, Booking, Comment  
        db.create_all()
 
    # Register 404 handler
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    # Register 500 handler
    @app.errorhandler(500)
    def internal_server_error(e):
        # Log the error for debugging
        app.logger.error(f"Internal Server Error: {e}")
        return render_template('500.html'), 500
    
    return app

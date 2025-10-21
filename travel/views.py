'''
Your directory should look like this:
project (folder)
 ├── main.py
 ├── travel (folder)
      ├── __init__.py
      ├── views.py
'''

'''
travel/views.py
'''
from flask import Blueprint,render_template, redirect, url_for, request, flash, session
from .forms import RegisterForm
from . import db
from .models import User
from flask_login import login_required, current_user

# Use of blue print to group routes, 
# name - first argument is the blue print name 
# import name - second argument - helps identify the root url for it 
mainbp = Blueprint('main', __name__)

@mainbp.route('/')
def index():
    print(session)
    session.pop('_flashes', None)
    
    from .models import Event
    # Show events that are Open or Sold Out (not Cancelled or Inactive)
    events = Event.query.filter(Event.status.in_(['Open', 'Sold Out'])).order_by(Event.event_date.desc()).limit(6).all()
    return render_template('index.html', events=events)

# REMOVED: The placeholder route for /bookings has been removed.
# @mainbp.route("/bookings")
# def bookings():
#     return render_template("bookings.html")

@mainbp.route("/about")
def about():
    return render_template("about.html")

@mainbp.route("/faq")
def faq():
    return render_template("FAQ.html")

@mainbp.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('profile.html'), 404
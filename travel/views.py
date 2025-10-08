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
from flask import Blueprint, render_template

# Use of blue print to group routes, 
# name - first argument is the blue print name 
# import name - second argument - helps identify the root url for it 
mainbp = Blueprint('main', __name__)

@mainbp.route('/')
def index():
    from .models import Event
    # Show events that are Open or Sold Out (not Cancelled or Inactive)
    events = Event.query.filter(Event.status.in_(['Open', 'Sold Out'])).order_by(Event.event_date.desc()).limit(6).all()
    return render_template('index.html', events=events)







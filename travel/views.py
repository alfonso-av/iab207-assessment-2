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
from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.utils import secure_filename
import os
import time

# Use of blue print to group routes, 
# name - first argument is the blue print name 
# import name - second argument - helps identify the root url for it 
mainbp = Blueprint('main', __name__)

@mainbp.route('/')
def index():
    from .models import Event
    # Show events that are Open or Sold Out (not Cancelled or Inactive)
    # Also filter out events with no tickets or all tickets sold out
    events = Event.query.filter(
        Event.status.in_(['Open', 'Sold Out'])
    ).order_by(Event.event_date.desc()).limit(6).all()
    
    # Filter out events where all tickets have 0 availability
    filtered_events = []
    for event in events:
        if event.tickets:
            total_availability = sum(ticket.availability for ticket in event.tickets)
            if total_availability > 0 or event.status == 'Sold Out':
                filtered_events.append(event)
        else:
            # Events with no tickets can still be shown if they're Open
            if event.status == 'Open':
                filtered_events.append(event)
    
    return render_template('index.html', events=filtered_events)

@mainbp.route('/bookings')
def bookings():
    """Display booking history page"""
    return render_template('bookings.html')

@mainbp.route('/edit-events')
def edit_events():
    """Display all events for editing"""
    from .models import Event
    events = Event.query.order_by(Event.event_date.desc()).all()
    return render_template('edit_events.html', events=events)

@mainbp.route('/login')
def login():
    """Display login page"""
    return render_template('login.html')






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

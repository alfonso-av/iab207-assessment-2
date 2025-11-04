from flask import Blueprint,render_template, redirect, url_for, request, flash, session, abort
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
    # Clear flash messages so they don't pile up
    session.pop('_flashes', None)
    from .models import Event

    # Update event statuses before loading the page
    Event.update_all_statuses()

    # Get the next 3 upcoming open events (top of the page)
    upcoming_events = (
        Event.query.filter_by(status='Open')
        .order_by(Event.event_date.asc())
        .limit(3)
        .all()
    )

    # Handle filters for the all events section
    sort_date = request.args.get('sort_date')
    category = request.args.get('category')
    status = request.args.get('status')

    events_query = Event.query

    if category:
        events_query = events_query.filter(Event.genres == category)
    if status:
        events_query = events_query.filter(Event.status == status)
    if sort_date == 'newest':
        events_query = events_query.order_by(Event.event_date.desc())
    elif sort_date == 'oldest':
        events_query = events_query.order_by(Event.event_date.asc())

    events = events_query.all()

    # Render homepage with both upcoming and filtered events
    return render_template(
        'index.html',
        open_events=upcoming_events,
        events=events,
        total_results=len(events),
        q=None
    )


@mainbp.route('/search')
def search():
    from .models import Event
    from sqlalchemy import or_

    # Get the text entered in the search bar
    q = request.args.get('q', '').strip()

    # Make sure statuses are up to date
    Event.update_all_statuses()

    # Show the same 3 upcoming open events at the top
    upcoming_events = (
        Event.query.filter_by(status='Open')
        .order_by(Event.event_date.asc())
        .limit(3)
        .all()
    )

    # Search across event name, artist, location, and description
    results = []
    if q:
        results = Event.query.filter(
            or_(
                Event.name.ilike(f"%{q}%"),
                Event.artist.ilike(f"%{q}%"),
                Event.location.ilike(f"%{q}%"),
                Event.description.ilike(f"%{q}%"),
            )
        ).all()

    # Render homepage with search results instead of filters
    return render_template(
        'index.html',
        open_events=upcoming_events,
        events=results,
        q=q,
        total_results=len(results)
    )




@mainbp.route('/edit-events')
@login_required
def edit_events():
    """Display only events created by the current user for editing"""
    from .models import Event
    
    # Update all event statuses based on current date/time
    Event.update_all_statuses()
    
    events = Event.query.filter_by(user_id=current_user.id).order_by(Event.event_date.desc()).all()
    return render_template('edit_events.html', events=events)

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

# testing for error 500
@mainbp.route('/force500')
def force500():
    abort(500)

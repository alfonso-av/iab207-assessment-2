from flask import Blueprint, render_template, request, redirect, url_for
from .models import db, Event, User, Booking
from datetime import datetime

mainbp = Blueprint("main", __name__)

# landing page
@mainbp.route("/")
def index():
    events = Event.query.all()
    return render_template("index.html", events=events)

# no logic yet
# TODO: /event/<int:event_id> to grab stored events in the database to populate and render in frontend
@mainbp.route("/event/<int:event_id>")
def event_details(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template("event_details.html", event=event)

# creates event and stores in the database. Still needs to have additional metadata to implement but works fine
@mainbp.route("/create_event", methods=["GET", "POST"])
def create_event():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        date = datetime.strptime(request.form["date"], "%Y-%m-%d")
        location = request.form["location"]

        new_event = Event(title=title, description=description, date=date, location=location)
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for("main.index"))
    return render_template("event_creation.html")


# no logic, just renders the html
# TODO: /bookings to show user bookings
@mainbp.route("/bookings")
def bookings():
    return render_template("bookings.html")

# TODO: /event_details to fetch info from database to render in web page
@mainbp.route("/event_details")
def event_details_page():
    return render_template("event_details.html")



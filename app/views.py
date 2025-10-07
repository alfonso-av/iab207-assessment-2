from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
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
@login_required
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

@mainbp.route('/Register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        existing_user = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email Address already exists.')
            return redirect('/Register')

        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'your bootstrap category[eg:success, primary, etc]')
        return redirect('/Log_In')
    return render_template('Register.html')

@mainbp.route('/Log_In', methods=['GET', 'POST'])
def login_page():
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect('/')
        else:
            flash('Invalid username or password')
    return render_template('Log_In.html')

@mainbp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('index.html')



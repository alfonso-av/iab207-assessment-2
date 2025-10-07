from . import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    bookings = db.relationship("Booking", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.name}>"


class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(150), nullable=False)
    image = db.Column(db.String(100), nullable=True, default="default.jpg")

    bookings = db.relationship("Booking", backref="event", lazy=True)

    def __repr__(self):
        return f"<Event {self.title}>"


class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)

    def __repr__(self):
        return f"<Booking user={self.user_id} event={self.event_id}>"

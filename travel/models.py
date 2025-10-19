from datetime import datetime
from flask_login import UserMixin
from . import db

class User(db.Model, UserMixin):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    emailid = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)#should be 128 in length to store hash

    def __repr__(self):
        return "<Email: {}, id: {}>".format(self.emailid, self.id)
    


class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    overview = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    genres = db.Column(db.String(200), nullable=False)
    image = db.Column(db.String(200), nullable=True)
    event_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Open', nullable=False)  # Open, Sold Out, Cancelled, Inactive

    # Foreign key relationship
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = db.relationship('User', backref='events')

    # Related models
    tickets = db.relationship('Ticket', backref='event', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='event', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Event {self.name} by {self.artist}>"

    # 🔄 Determine the *correct* current status based on real-time conditions
    def get_dynamic_status(self):
        now = datetime.now()

        # Cancelled always takes highest priority
        if self.status and self.status.lower() == "cancelled":
            return "Cancelled"

        # Sold Out next priority
        if self.status and self.status.lower() == "sold out":
            return "Sold Out"

        # Check if event has ended
        if self.event_date and self.end_time:
            event_end = datetime.combine(self.event_date, self.end_time)
            if event_end < now:
                return "Inactive"

        # Otherwise, still open
        return "Open"

    # 🧠 Persist a corrected status in the DB if out of sync
    def update_status(self):
        """Compare current and computed status; sync DB if needed."""
        new_status = self.get_dynamic_status()
        if new_status != self.status:
            self.status = new_status
            db.session.commit()

    # 📊 Shortcut property — access in templates via {{ event.dynamic_status }}
    @property
    def dynamic_status(self):
        """Return up-to-date event status based on time, tickets, and cancellation."""
        return self.get_dynamic_status()

class Ticket(db.Model):
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    availability = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    
    def __repr__(self):
        return f"Ticket: {self.name} - ${self.price}"

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    
    def __repr__(self):
        return f"Comment by {self.author}: {self.text[:50]}..."

# Legacy classes for backward compatibility
class Events:
    def __init__(self, name, description, image, currency):
        self.name = name
        self.description = description
        self.image = image
        self.currency = currency
        self.comments = list()

    def set_comments(self, comment):
        self.comments.append(comment)

    def __repr__(self):
        return f"Name: {self.name}, Currency: {self.currency}"

class Destination:
    def __init__(self, name, description, image, currency):
        self.name = name
        self.description = description
        self.image = image
        self.currency = currency
        self.comments = list()

    def set_comments(self, comment):
        self.comments.append(comment)

    def __repr__(self):
        return f"Name: {self.name}, Currency: {self.currency}"
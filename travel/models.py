from datetime import datetime
from . import db

class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    overview = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    genres = db.Column(db.String(200), nullable=False)  # Store as comma-separated string
    image = db.Column(db.String(200), nullable=True)
    event_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Open', nullable=False)  # Open, Sold Out, Cancelled, Inactive
    
    # Relationship with tickets
    tickets = db.relationship('Ticket', backref='event', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='event', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"Event: {self.name} by {self.artist}"

class Ticket(db.Model):
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    availability = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Available', nullable=False)  # Available, Sold Out
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
# Imports for Flask, SQLAlchemy, Forms, and Security
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash # Required authentication library
from sqlalchemy import func
from forms import (
    LoginForm, RegisterForm, EventForm, TicketForm, CommentForm,
    # Additional imports for form classes from your forms.py
) 
from models import (
    db, User, Event, Ticket, Booking, Comment,
    # Import all models
)

# --- Configuration Setup ---
# Initialize Flask app
app = Flask(__name__)

# Load configuration from environment variables or use defaults
# NOTE: The database file is placed in the project's root folder
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key_change_me')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///events.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
csrf = CSRFProtect(app)
# Flask-Login initialization is omitted for now, as requested.

# Import Bootstrap-Flask for template rendering
from flask_bootstrap import Bootstrap5
bootstrap = Bootstrap5(app)



# --- Utility Functions (For demonstration, will move to auth blueprint later) ---

def create_initial_data(app):
    """Creates a default user and initial event data for testing."""
    with app.app_context():
        # Check if DB tables exist
        if not db.engine.inspect(db.engine).has_table("users"):
            db.create_all()

        # Create a test user if one doesn't exist
        if not User.query.filter_by(emailid='test@test.com').first():
            test_user = User(
                first_name='Test',
                surname='User',
                emailid='test@test.com',
                phone='555-1234',
                address='123 Main St',
                password_hash=generate_password_hash('password123', method='pbkdf2:sha256')
            )
            db.session.add(test_user)
            db.session.commit()
            print("Test user created.")

        # Create a test event if one doesn't exist
        if not Event.query.filter_by(name='Gorillaz World Tour').first():
            event1 = Event(
                name='Gorillaz World Tour',
                artist='Gorillaz',
                overview='The virtual band embarks on a world-spanning tour.',
                location='Sydney Opera House, Sydney, AU',
                description='A mesmerizing fusion of animation and live music, featuring classic hits and new tracks from their latest album.',
                genres='Electronic, Alternative Rock',
                image='gorillaz.jpg',
                event_date=datetime(2025, 12, 10, 20, 0, 0),
                status='Open',
                user_id=test_user.id
            )
            db.session.add(event1)
            db.session.commit()

            # Create tickets for the event
            ticket1 = Ticket(
                event_id=event1.id,
                name='General Admission',
                price=89.99,
                availability=500,
                description='Standard entry ticket.'
            )
            ticket2 = Ticket(
                event_id=event1.id,
                name='VIP Package',
                price=199.99,
                availability=50,
                description='Includes priority entry and exclusive merchandise.'
            )
            db.session.add_all([ticket1, ticket2])
            db.session.commit()
            print("Test event and tickets created.")


# --- Test/Utility Route for Database Initialization ---
@app.route('/init_db')
def init_db_route():
    """Initializes the database with test data."""
    create_initial_data(app)
    flash("Database initialized with test data and user 'test@test.com' (password: password123).", 'info')
    return redirect(url_for('main.index'))

# --- Main Booking Logic (Simplified for demonstration) ---
# NOTE: This route should be secured with @login_required later.
# For now, we hardcode user_id=1 as per the initial test data.
@app.route('/book_tickets', methods=['POST'])
def book_tickets():
    """Handles the ticket purchase form submission."""
    # NOTE: Hardcoding user_id=1 for now.
    user_id = 1 

    # Get event ID from hidden field or request arguments
    event_id = request.form.get('event_id', type=int)
    if not event_id:
        flash("Event ID missing.", 'danger')
        return redirect(url_for('main.index'))

    # Start transaction
    try:
        # Loop through form data to find selected tickets
        for key, value in request.form.items():
            if key.startswith('quantity_') and int(value) > 0:
                ticket_id = int(key.split('_')[1])
                quantity = int(value)

                # Fetch ticket (and lock it if possible in a real app)
                ticket = Ticket.query.filter_by(id=ticket_id, event_id=event_id).with_for_update().first()
                
                if not ticket:
                    flash("Invalid ticket selected.", 'danger')
                    return redirect(url_for('event_detail', event_id=event_id))

                if quantity > ticket.availability:
                    flash(f"Requested quantity ({quantity}) exceeds available stock ({ticket.availability}) for {ticket.name}.", 'danger')
                    return redirect(url_for('event_detail', event_id=event_id))

                # 1. Reduce Stock
                ticket.availability -= quantity
                
                # 2. Create Booking
                new_booking = Booking(
                    user_id=user_id,
                    event_id=event_id,
                    ticket_id=ticket.id,
                    quantity=quantity
                )
                db.session.add(new_booking)

                # Commit the changes (stock reduction and booking creation) together
                db.session.commit()
                
                flash(f"Successfully booked {quantity} x {ticket.name}. Your Order ID is #{new_booking.id}", 'success')
                # Return the order detail (Order ID) for reference, as required by the CRA
                
                # IMPORTANT: Redirect to the new, official booking history route
                return redirect(url_for('bookings.history')) 

        # If no tickets were selected
        flash("Please select at least one ticket quantity.", 'danger')
        return redirect(url_for('event_detail', event_id=event_id))


    except Exception as e:
        db.session.rollback()
        print(f"Booking transaction failed: {e}")
        flash("An unexpected error occurred during booking. Please try again.", 'danger')
        return redirect(url_for('event_detail', event_id=event_id))


# --- REMOVED TEMPORARY my_bookings ROUTE ---
# The /my_bookings route logic is now handled by the bookings blueprint (bookings.py)


# --- Register Blueprints (Placeholder for event_detail until proper blueprints are set up) ---

@app.route('/event/<int:event_id>')
def event_detail(event_id):
    from .models import Event, Ticket, Comment
    # Fetch event and its related tickets/comments
    event = Event.query.get_or_404(event_id)
    tickets = Ticket.query.filter_by(event_id=event.id).all()
    comments = Comment.query.filter_by(event_id=event.id).order_by(Comment.created_at.desc()).all()
    
    # Placeholder form instance
    from forms import CommentForm # Import locally to avoid circular dependency issues during early development
    comment_form = CommentForm()

    return render_template('event_details.html', event=event, tickets=tickets, comments=comments, comment_form=comment_form)

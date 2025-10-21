from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from werkzeug.utils import secure_filename
import os
import time 
from datetime import datetime 
from .models import db, Event, Ticket, Comment, Booking, User, Destination 
from .forms import EventForm, TicketForm, CommentForm, DestinationForm 
from flask_login import login_required, current_user
from sqlalchemy import or_

# Use of blueprint to group routes, 
# name - first argument is the blue print name 
# import name - second argument - helps identify the root url for it 

def update_event_status_based_on_tickets(event):
    """Helper function to update event status based on ticket availability"""
    if not event.tickets:
        # No tickets = Open
        event.status = 'Open'
        return
    
    # Check if all tickets are sold out
    all_tickets_sold_out = all(ticket.availability == 0 for ticket in event.tickets)
    if all_tickets_sold_out:
        event.status = 'Sold Out'
    else:
        # Some tickets available = Open (unless manually set otherwise)
        if event.status not in ['Cancelled', 'Inactive']:
            event.status = 'Open'



eventbp = Blueprint('events', __name__, url_prefix='/events')



@eventbp.route('/search')
def search():
    query = request.args.get('q', '').strip()  # what user typed
    if not query:
        events = Event.query.all()
    else:
        events = Event.query.filter(
            or_(
                Event.name.ilike(f"%{query}%"),
                Event.artist.ilike(f"%{query}%"),
                Event.genres.ilike(f"%{query}%"),
                Event.location.ilike(f"%{query}%"),
            )
        ).all()

    return render_template('all_events.html', events=events, query=query)


@eventbp.route('/<int:event_id>/book', methods=['POST'])
@login_required
def process_booking(event_id):
    """
    Processes the ticket booking form submission.
    """
    event = Event.query.get_or_404(event_id)
    form_data = request.form
    
    user_id = current_user.id
    total_quantity = 0

    try:
        # Loop through form data to find all requested ticket quantities
        for key, value in form_data.items():
            if key.startswith('quantity_') and value.isdigit():
                ticket_id = key.split('_')[1]
                quantity = int(value)

                if quantity > 0:
                    ticket = Ticket.query.get(ticket_id)
                    
                    if not ticket or ticket.event_id != event.id:
                        flash("Invalid ticket selected.", 'danger')
                        continue
                    
                    if quantity > ticket.availability:
                        flash(f"Only {ticket.availability} tickets left for {ticket.name}. Requested {quantity}.", 'danger')
                        continue
                    
                    # Reduce Stock
                    ticket.availability -= quantity 
                    
                    # Update ticket status based on new availability
                    ticket.update_status()
                    
                    booking_price = quantity * ticket.price
                    
                    # Create Bookings record
                    new_booking = Booking(
                        user_id=user_id,
                        event_id=event_id,
                        ticket_id=ticket.id,
                        quantity=quantity,
                        total_price=booking_price,
                        booked_at=datetime.utcnow() 
                    )
                    db.session.add(new_booking)
                    total_quantity += quantity

        if total_quantity == 0:
            flash("You must select at least one ticket to proceed.", 'warning')
            return redirect(url_for('events.show', id=event_id))

        # Commit saves BOTH the new booking AND the reduced ticket availability
        db.session.commit() 
        
        flash(f"Successfully booked {total_quantity} tickets for {event.name}!", 'success')


        return redirect(url_for('bookings.history')) 

    except Exception as e:
        db.session.rollback()
        print(f"Booking transaction failed: {e}")
        flash("An unexpected error occurred during booking. Please try again.", 'danger')
        return redirect(url_for('events.show', id=event_id))
    
@eventbp.route('/cancel_booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    """Handles the cancellation of a user's booking by deleting the record."""
    from .models import Booking, db # Ensure models are imported

    booking_to_cancel = Booking.query.get_or_404(booking_id)

    if booking_to_cancel.user_id != current_user.id:
        flash('You do not have permission to cancel this booking.', 'danger')
        return redirect(url_for('bookings.history')) 

    try:
        # Re-increment ticket availability
        ticket = booking_to_cancel.ticket
        ticket.availability += booking_to_cancel.quantity
        
        # Update ticket status based on new availability
        ticket.update_status()
        
        db.session.add(ticket)
        
        # Delete the booking record
        db.session.delete(booking_to_cancel)
        db.session.commit()
        flash(f'Booking  cancelled.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred during cancellation. Please try again.', 'danger')


    return redirect(url_for('bookings.history'))





#  ------------------- Razia ------------------------------------

@eventbp.route('/')
def list_all():
    """Display all events"""
    # Update all event statuses based on current date/time
    Event.update_all_statuses()
    
    # Show only active events (Open and Sold Out), ordered by date
    events = Event.query.filter(Event.status.in_(['Open', 'Sold Out'])).order_by(Event.event_date.asc()).all()
    return render_template('all_events.html', events=events)


@eventbp.route('/<int:id>')
def show(id):

    """Show event details, including tickets and comments"""
    event = Event.query.get_or_404(id)
    comment_form = CommentForm()
    # Fetch all associated tickets for display on the detail page
    tickets = Ticket.query.filter_by(event_id=event.id).order_by(Ticket.price).all()
    # Fetch all associated comments, ordered by newest first
    comments = Comment.query.filter_by(event_id=event.id).order_by(Comment.created_at.desc()).all()
    if current_user.is_authenticated:
        comment_form.author.data = f"{current_user.first_name} {current_user.surname}"     
    return render_template('event_details.html', event=event, comment_form=comment_form, tickets=tickets, comments=comments )


@eventbp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new event"""
    form = EventForm()
    
    # For GET requests, ensure form is clean (no validation errors)
    if request.method == 'GET':
        form = EventForm()  # Create a fresh form instance
        # Clear any potential errors from previous submissions
        form.errors.clear()
    
    # Debug: Check database connection and table structure
    try:
        from .models import Event
        event_count = Event.query.count()
        print(f"Database connection OK. Current event count: {event_count}")
    except Exception as db_error:
        print(f"Database connection error: {db_error}")
    
    # post request 
    print(f"Form submitted. Method: {request.method}")
    print(f"Form validation result: {form.validate()}")
    print(f"Form errors: {form.errors}")
    print(f"Current user: {current_user.id if current_user.is_authenticated else 'Not authenticated'}")
    
    if form.validate_on_submit():
        print(f"Form validation passed for user: {current_user.id} ({current_user.first_name})")
        try:
            # Handle file upload
            image_filename = None
            if form.image.data:
                image = form.image.data
                filename = secure_filename(image.filename)
                
                # If secure_filename removes everything, use a fallback
                if not filename or len(filename) == 0:
                    # Get file extension
                    original_name = image.filename
                    if '.' in original_name:
                        ext = original_name.split('.')[-1].lower()
                        filename = f"event_image_{int(time.time())}.{ext}"
                    else:
                        filename = f"event_image_{int(time.time())}.jpg"
                
                if filename:
                    # Create uploads directory if it doesn't exist
                    # current_app.root_path points to the travel directory, so we need to go up one level
                    project_root = os.path.dirname(current_app.root_path)
                    upload_dir = os.path.join(project_root, 'static', 'uploads')
                    os.makedirs(upload_dir, exist_ok=True)
                    image_filename = filename
                    full_path = os.path.join(upload_dir, filename)
                    image.save(full_path)
                    print(f"Image saved to: {full_path}")
            
            # Create event
            event = Event(
                name=form.name.data,
                artist=form.artist.data,
                overview=form.overview.data,
                location=form.location.data,
                description=form.description.data,
                genres=','.join(form.genres.data) if form.genres.data else '',
                image=image_filename,
                event_date=form.event_date.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data,
                status=form.status.data,
                user_id=current_user.id  # Assign the current user as the event creator
            )
            
            print(f"About to add event to database: {event.name} by {event.artist}")
            db.session.add(event)
            db.session.flush()  # Get the event ID
            print(f"Created event with ID: {event.id}, User ID: {event.user_id}")
            print(f"Event data: name={event.name}, artist={event.artist}, location={event.location}")
            
            # Handle ticket data
            ticket_names = request.form.getlist('ticket_names')
            ticket_prices = request.form.getlist('ticket_prices')
            ticket_availabilities = request.form.getlist('ticket_availabilities')
            ticket_descriptions = request.form.getlist('ticket_descriptions')
            
            # Create tickets if any were added
            if ticket_names and ticket_prices and ticket_availabilities and ticket_descriptions:
                for i in range(len(ticket_names)):
                    if ticket_names[i] and ticket_prices[i] and ticket_availabilities[i] and ticket_descriptions[i]:
                        availability = int(ticket_availabilities[i])
                        
                        # Set initial ticket status based on availability
                        ticket_status = 'Available' if availability > 0 else 'Sold Out'
                        
                        ticket = Ticket(
                            name=ticket_names[i],
                            price=float(ticket_prices[i]),
                            availability=int(ticket_availabilities[i]),
                            description=ticket_descriptions[i],
                            event_id=event.id
                        )
                        db.session.add(ticket)
            
            # Update event status based on all tickets
            update_event_status_based_on_tickets(event)
            print(f"Updated new event {event.id} status to: {event.status}")
            
            db.session.commit()
            print(f"Event {event.id} successfully committed to database")
            
            flash('Event created successfully!', 'success')
            print(f"Redirecting to event details page for event {event.id}")
            return redirect(url_for('events.show', id=event.id))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating event: {str(e)}")
            flash(f'Error creating event: {str(e)}', 'error')
    else:
        print(f"Form validation failed. Errors: {form.errors}")
    
    # get request 
    return render_template('event_creation.html', form=form)



@eventbp.route('/test-create', methods=['GET'])
@login_required
def test_create():
    """Test route to manually create an event for debugging"""
    try:
        from .models import Event
        from datetime import datetime, date, time
        
        # Create a simple test event
        test_event = Event(
            name="Test Event",
            artist="Test Artist",
            overview="Test overview",
            location="Test Location",
            description="Test description",
            genres="Rock",
            event_date=date(2025, 12, 25),
            start_time=time(20, 0),
            end_time=time(23, 0),
            status="Open",
            user_id=current_user.id
        )
        
        db.session.add(test_event)
        db.session.commit()
        
        return f"Test event created successfully! Event ID: {test_event.id}, User ID: {test_event.user_id}"
        
    except Exception as e:
        return f"Error creating test event: {str(e)}"

@eventbp.route('/migrate-ticket-status', methods=['GET'])
@login_required
def migrate_ticket_status():
    """Migration route to add status column to tickets table and update existing tickets"""
    try:
        from .models import Ticket
        from sqlalchemy import text
        
        # First, add the status column to the tickets table if it doesn't exist
        try:
            # Check if the column already exists
            result = db.session.execute(text("PRAGMA table_info(tickets)"))
            columns = [row[1] for row in result.fetchall()]
            
            if 'status' not in columns:
                # Add the status column
                db.session.execute(text("ALTER TABLE tickets ADD COLUMN status VARCHAR(20) DEFAULT 'Available'"))
                print("Added status column to tickets table")
            else:
                print("Status column already exists in tickets table")
                
        except Exception as col_error:
            print(f"Error adding column: {col_error}")
            return f"Error adding status column: {str(col_error)}"
        
        # Now update existing tickets that might have NULL status
        tickets = Ticket.query.filter(Ticket.status.is_(None)).all()
        
        if not tickets:
            return "Migration completed! Status column added. No existing tickets needed updating."
        
        updated_count = 0
        for ticket in tickets:
            # Set status based on availability
            if ticket.availability <= 0:
                ticket.status = 'Unavailable'
            else:
                ticket.status = 'Available'
            updated_count += 1
        
        db.session.commit()
        
        return f"Migration completed! Added status column and updated {updated_count} existing tickets."
        


    except Exception as e:
        db.session.rollback()
        return f"Migration failed: {str(e)}"


@eventbp.route('/add-status-column', methods=['GET'])
def add_status_column():
    """Simple route to add status column to tickets table"""
    try:
        from sqlalchemy import text
        
        # Add the status column to the tickets table
        db.session.execute(text("ALTER TABLE tickets ADD COLUMN status VARCHAR(20) DEFAULT 'Available'"))
        db.session.commit()
        
        return "Status column added successfully to tickets table!"
        
    except Exception as e:
        db.session.rollback()
        return f"Error adding status column: {str(e)}"




@eventbp.route('/all', methods=['GET'])
def all_events():
    query = request.args.get('query', '')
    sort_date = request.args.get('sort_date')
    sort_alpha = request.args.get('sort_alpha')
    category = request.args.get('category')
    status = request.args.get('status')
    
    # Update all event statuses based on current date/time first
    Event.update_all_statuses()
    
    events = Event.query

    # search query
    if query:
        events = events.filter(Event.name.ilike(f"%{query}%"))

    # genre filter
    if category:
        events = events.filter(Event.genres.ilike(f"%{category}%"))

    # Status filter
    if status:
        events = events.filter(Event.status.ilike(f"%{status}%"))
    else:
        # By default, only show active events (Open, Sold Out) - exclude Inactive and Cancelled
        events = events.filter(Event.status.in_(['Open', 'Sold Out']))

    # sorting options
    if sort_date == "newest":
        events = events.order_by(Event.event_date.desc())
    elif sort_date == "oldest":
        events = events.order_by(Event.event_date.asc())
    elif sort_alpha == "az":
        events = events.order_by(Event.name.asc())
    elif sort_alpha == "za":
        events = events.order_by(Event.name.desc())

    events = events.all()

    return render_template('all_events.html', events=events, query=query)


@eventbp.route('/<int:event_id>/add_ticket', methods=['POST'])
@login_required
def add_ticket(event_id):
    """Add a ticket to an event"""
    event = Event.query.get_or_404(event_id)
    form = TicketForm()
    
    if form.validate_on_submit():
        try:
            ticket = Ticket(
                name=form.name.data,
                price=form.price.data,
                availability=form.availability.data,
                description=form.description.data,
                event_id=event_id
            )
            
            db.session.add(ticket)
            db.session.commit()
            
            flash('Ticket added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding ticket: {str(e)}', 'error')
    
    return redirect(url_for('events.show', id=event_id))


@eventbp.route('/<int:id>/add_comment', methods=['POST'])
@login_required
def add_comment(id):
    """Add a comment to an event"""
    event = Event.query.get_or_404(id)
    form = CommentForm()
    
    if form.validate_on_submit():
        try:
            # Automatically set author to current user's name
            author_name = f"{current_user.first_name} {current_user.surname}"
            
            comment = Comment(
                text=form.text.data,
                author=author_name,
                event_id=id,
                created_at=datetime.now()  # Use local time
            )
            
            db.session.add(comment)
            db.session.commit()
            
            flash('Comment added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding comment: {str(e)}', 'error')
    
    return redirect(url_for('events.show', id=id))



@eventbp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit an existing event"""
    event = Event.query.get_or_404(id)
    
    # Check if the current user owns this event
    if event.user_id != current_user.id:
        flash('You can only edit events that you created.', 'danger')
        return redirect(url_for('main.edit_events'))
    
    form = EventForm()
    
    print(f"Request method: {request.method}")
    if request.method == 'POST':
        print(f"POST request received for event {id}")
        print(f"Form data: {request.form}")
        print(f"Form validation: {form.validate()}")
        if not form.validate():
            print(f"Form errors: {form.errors}")
        
        # Check if this is a cancellation request first (before form validation)
        if request.form.get('status') == 'Cancelled':
            print(f"Event {id} is being cancelled - deleting event")
            try:
                db.session.delete(event)
                db.session.commit()
                flash('Event has been cancelled and deleted.', 'success')
                return redirect(url_for('main.edit_events'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error cancelling event: {str(e)}', 'error')
                return redirect(url_for('events.edit', id=id))
    else:
        # Pre-populate form fields manually (excluding image field) for GET requests
        form.name.data = event.name
        form.artist.data = event.artist
        form.overview.data = event.overview
        form.location.data = event.location
        form.description.data = event.description
        form.event_date.data = event.event_date
        form.start_time.data = event.start_time
        form.end_time.data = event.end_time
        form.status.data = event.status
        
        # Pre-populate genres from the comma-separated string
        if event.genres:
            form.genres.data = event.genres.split(',')
            print(f"Genres populated: {form.genres.data}")
        else:
            print(f"No genres found for event")
    
    if form.validate_on_submit():
        print(f"Form validated successfully for edit")
        print(f"Name: {form.name.data}")
        print(f"Artist: {form.artist.data}")
        print(f"Genres: {form.genres.data}")
        try:
            # Handle file upload
            if form.image.data and hasattr(form.image.data, 'filename') and form.image.data.filename:
                try:
                    image = form.image.data
                    filename = secure_filename(image.filename)
                    
                    # If secure_filename removes everything, use a fallback
                    if not filename or len(filename) == 0:
                        # Get file extension
                        original_name = image.filename
                        if '.' in original_name:
                            ext = original_name.split('.')[-1].lower()
                            filename = f"event_image_{int(time.time())}.{ext}"
                        else:
                            filename = f"event_image_{int(time.time())}.jpg"
                    
                    if filename:
                        # Create uploads directory if it doesn't exist
                        project_root = os.path.dirname(current_app.root_path)
                        upload_dir = os.path.join(project_root, 'static', 'uploads')
                        os.makedirs(upload_dir, exist_ok=True)
                        
                        # Delete old image if it exists
                        if event.image:
                            old_image_path = os.path.join(upload_dir, event.image)
                            if os.path.exists(old_image_path):
                                os.remove(old_image_path)
                        
                        # Save new image
                        full_path = os.path.join(upload_dir, filename)
                        image.save(full_path)
                        event.image = filename
                        print(f"Image saved to: {full_path}")
                except Exception as img_error:
                    print(f"Error handling image upload: {str(img_error)}")
                    print(f"Image data type: {type(form.image.data)}")
                    print(f"Image data: {form.image.data}")
                    # Continue without updating the image
            
            # Update event fields
            print(f"Updating event fields...")
            print(f"Old name: {event.name}")
            print(f"New name: {form.name.data}")
            
            event.name = form.name.data
            event.artist = form.artist.data
            event.overview = form.overview.data
            event.location = form.location.data
            event.description = form.description.data
            event.genres = ','.join(form.genres.data) if form.genres.data else ''
            event.event_date = form.event_date.data
            event.start_time = form.start_time.data
            event.end_time = form.end_time.data
            
            event.status = form.status.data
            
            # Check if all tickets have 0 availability and auto-set to Sold Out
            total_availability = sum(ticket.availability for ticket in event.tickets)
            if total_availability == 0 and event.tickets:
                print(f"All tickets sold out for event {event.id} - setting status to Sold Out")
                event.status = 'Sold Out'
            
            print(f"Event name after update: {event.name}")
            db.session.commit()
            print(f"Database committed successfully")
            
            flash('Event updated successfully!', 'success')
            return redirect(url_for('events.show', id=event.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating event: {str(e)}', 'error')
    else:
        print(f"Form validation failed")
        print(f"Form errors: {form.errors}")
        for field, errors in form.errors.items():
            print(f"Field {field}: {errors}")
    
    return render_template('edit_event.html', form=form, event=event)

@eventbp.route('/tickets/<int:ticket_id>/edit', methods=['POST'])
@login_required
def edit_ticket(ticket_id):
    """Edit an existing ticket"""
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Check if the current user owns the event this ticket belongs to
    if ticket.event.user_id != current_user.id:
        flash('You can only edit tickets for events that you created.', 'danger')
        return redirect(url_for('main.edit_events'))
    
    try:
        # Update ticket fields
        ticket.name = request.form.get('name')
        ticket.price = float(request.form.get('price'))
        ticket.availability = int(request.form.get('availability'))
        ticket.description = request.form.get('description')
        
        # Auto-update ticket status based on availability
        ticket.update_status()
        
        # Update event status based on all tickets
        update_event_status_based_on_tickets(ticket.event)
        print(f"Updated event {ticket.event.id} status to: {ticket.event.status}")
        
        db.session.commit()
        flash('Ticket updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating ticket: {str(e)}', 'error')
    
    return redirect(url_for('events.edit', id=ticket.event_id))

@eventbp.route('/tickets/<int:ticket_id>/delete', methods=['GET'])
@login_required
def delete_ticket(ticket_id):
    """Delete a ticket"""
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Check if the current user owns the event this ticket belongs to
    if ticket.event.user_id != current_user.id:
        flash('You can only delete tickets for events that you created.', 'danger')
        return redirect(url_for('main.edit_events'))
    
    event_id = ticket.event_id
    
    try:
        db.session.delete(ticket)
        
        # Update event status based on remaining tickets
        event = ticket.event
        update_event_status_based_on_tickets(event)
        print(f"Updated event {event_id} status to: {event.status}")
        
        db.session.commit()
        flash('Ticket deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting ticket: {str(e)}', 'error')
    
    return redirect(url_for('events.edit', id=event_id))









# ------------------------------------------------------------------
# Legacy destination routes for backward compatibility
destbp = Blueprint('destination', __name__, url_prefix='/destinations')

@destbp.route('/<id>')
def show_destination(id):
    destination = get_destination()
    return render_template('destinations/show.html', destination=destination)

@destbp.route('/create', methods = ['GET', 'POST'])
def create_destination():
    from .forms import DestinationForm
    print('Method type: ', request.method)
    form = DestinationForm()
    if form.validate_on_submit():
        print('Successfully created new travel destination')
        # return redirect(url_for('destination.create'))
    return render_template('destinations/create.html', form=form)

def get_destination():
    from .models import Destination, Comment
    # creating the description of Brazil
    b_desc = """Brazil is considered an advanced emerging economy.
     It has the ninth largest GDP in the world by nominal, and eight by PPP measures. 
     It is one of the world\'s major breadbaskets, being the largest producer of coffee for the last 150 years."""
     # an image location
    image_loc = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQFyC8pBJI2AAHLpAVih41_yWx2xxLleTtdshAdk1HOZQd9ZM8-Ag'
    destination = Destination('Brazil', b_desc,image_loc, 'R$10')
    # a comment
    comment = Comment("Sam", "Visited during the olympics, was great", '2023-08-12 11:00:00')
    destination.set_comments(comment)
    comment = Comment("Bill", "free food!", '2023-08-12 11:00:00')
    destination.set_comments(comment)
    comment = Comment("Sally", "free face masks!", '2023-08-12 11:00:00')
    destination.set_comments(comment)
    return destination


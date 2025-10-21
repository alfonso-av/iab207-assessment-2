from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from .models import db, Booking, Event, Ticket 

# Define the Blueprint
bookingsbp = Blueprint('bookings', __name__, url_prefix='/bookings')

# FIX: Change the route to the root path of the blueprint ('/'), which corresponds to /bookings
@bookingsbp.route('/') 
@login_required
def history():
    """
    Retrieves and displays the booking history for the current logged-in user.
    """
    
    # Query all bookings for the current user, ordered by the most recent first.
    user_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booked_at.desc()).all()
    
    # Renders the dynamic template
    return render_template('bookings.html', bookings=user_bookings) 


@bookingsbp.route('/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    """
    Handles the cancellation of a specific booking.
    """
    # 1. Fetch the booking or return 404
    booking = Booking.query.get_or_404(booking_id)

    # 2. Security Check: Ensure the current user owns this booking
    if booking.user_id != current_user.id:
        flash("You do not have permission to cancel this booking.", 'danger')
        # FIX: Redirect to the correct endpoint name: 'bookings.history'
        return redirect(url_for('bookings.history')) 

    # 3. Increase Ticket Availability (Reverse the stock reduction)
    ticket = Ticket.query.get(booking.ticket_id)
    if ticket:
        ticket.availability += booking.quantity
        # Update ticket status based on new availability
        ticket.update_status()
    
    # 4. Delete the Booking Record
    db.session.delete(booking)
    
    try:
        db.session.commit()
        flash(f"Booking #{booking_id} for {booking.quantity} tickets successfully cancelled.", 'success')
    except Exception as e:
        db.session.rollback()
        flash("An error occurred during cancellation.", 'danger')

    # FIX: Redirect to the correct endpoint name: 'bookings.history'
    return redirect(url_for('bookings.history'))
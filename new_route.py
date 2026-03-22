# ============================================================
# ADD THESE IMPORTS to the top of your app.py
# ============================================================
# from models import db, Event, Registration, HourLog, Review
# from forms import ..., VerifyAttendanceForm, ReviewForm
# from flask_login import login_required, current_user
# from datetime import datetime


# ============================================================
# ROUTE 1 — Volunteer verifies attendance & logs hours via code
# POST /events/<event_id>/verify
# ============================================================

@app.route('/events/<int:event_id>/verify', methods=['GET', 'POST'])
@login_required          # remove decorator if you're not using Flask-Login yet
def verify_attendance(event_id):
    """
    The volunteer opens this page for a specific event, enters the
    6-character code the supervisor displayed, and logs their hours.

    What happens on a valid code:
      1. Registration.attendance_verified is set to True.
      2. A HourLog is created with status='verified' (auto-approved).
         No supervisor review step required.

    What happens on an invalid code:
      The form is re-shown with an error message.
    """
    event = Event.query.get_or_404(event_id)
    form = VerifyAttendanceForm()

    # Make sure the student is actually registered for this event
    registration = Registration.query.filter_by(
        student_id=current_user.id,
        event_id=event_id
    ).first()

    if not registration:
        flash('You are not registered for this event.', 'danger')
        return redirect(url_for('events'))

    # Prevent double-verification
    if registration.attendance_verified:
        flash('Your attendance for this event has already been verified.', 'info')
        return redirect(url_for('events'))

    if form.validate_on_submit():
        # --- Check the code (case-insensitive) ---
        entered_code = form.verification_code.data.strip().upper()
        if entered_code != event.verification_code.upper():
            flash('Invalid verification code. Please check with your supervisor.', 'danger')
            return render_template('verify_attendance.html', form=form, event=event)

        # --- Mark attendance as verified ---
        registration.attendance_verified = True
        registration.verified_at = datetime.utcnow()

        # --- Create auto-approved HourLog ---
        # Check if a log already exists (edge case)
        existing_log = HourLog.query.filter_by(
            student_id=current_user.id,
            event_id=event_id
        ).first()

        if existing_log:
            # Update the existing log instead of creating a duplicate
            existing_log.hours = form.hours.data
            existing_log.description = form.description.data
            existing_log.status = 'verified'
            existing_log.verified_by_code = True
            existing_log.reviewed_at = datetime.utcnow()
        else:
            new_log = HourLog(
                student_id=current_user.id,
                event_id=event_id,
                hours=form.hours.data,
                description=form.description.data,
                status='verified',          # auto-approved — no manual review needed
                verified_by_code=True,
                reviewed_at=datetime.utcnow()
            )
            db.session.add(new_log)

        db.session.commit()
        flash(
            f'Attendance verified! {form.hours.data} hours logged for "{event.title}".',
            'success'
        )
        return redirect(url_for('events'))

    return render_template('verify_attendance.html', form=form, event=event)


# ============================================================
# ROUTE 2 — Supervisor regenerates the code (optional but useful)
# POST /events/<event_id>/regenerate-code
# ============================================================

@app.route('/events/<int:event_id>/regenerate-code', methods=['POST'])
@login_required
def regenerate_verification_code(event_id):
    """
    Allows a supervisor (or admin) to generate a fresh code for an event,
    for example if the previous code was shared too widely.
    """
    event = Event.query.get_or_404(event_id)

    # Only the assigned supervisor or an admin can regenerate
    if current_user.role not in ('supervisor', 'admin') and event.supervisor_id != current_user.id:
        flash('You do not have permission to do this.', 'danger')
        return redirect(url_for('events'))

    from models import generate_verification_code
    event.verification_code = generate_verification_code()
    db.session.commit()
    flash(f'New verification code generated: {event.verification_code}', 'success')
    return redirect(url_for('event_detail', event_id=event_id))  # adjust url_for to your detail route


# ============================================================
# ROUTE 3 — Submit a review for an event
# GET/POST /events/<event_id>/review
# ============================================================

@app.route('/events/<int:event_id>/review', methods=['GET', 'POST'])
@login_required
def submit_review(event_id):
    """
    A volunteer can write a review only if they have a verified or
    approved HourLog for this event.  One review per student per event.
    """
    event = Event.query.get_or_404(event_id)

    # Guard: student must have participated (approved or verified hours)
    hour_log = HourLog.query.filter(
        HourLog.student_id == current_user.id,
        HourLog.event_id == event_id,
        HourLog.status.in_(['approved', 'verified'])
    ).first()

    if not hour_log:
        flash('You can only review events you have participated in and had hours approved.', 'warning')
        return redirect(url_for('events'))

    # Guard: one review per student per event
    existing_review = Review.query.filter_by(
        student_id=current_user.id,
        event_id=event_id
    ).first()

    if existing_review:
        flash('You have already submitted a review for this event.', 'info')
        return redirect(url_for('event_reviews', event_id=event_id))

    form = ReviewForm()

    if form.validate_on_submit():
        review = Review(
            student_id=current_user.id,
            event_id=event_id,
            rating=int(form.rating.data),
            body=form.body.data
        )
        db.session.add(review)
        db.session.commit()
        flash('Thank you for your review!', 'success')
        return redirect(url_for('event_reviews', event_id=event_id))

    return render_template('submit_review.html', form=form, event=event)


# ============================================================
# ROUTE 4 — View all reviews for an event (public)
# GET /events/<event_id>/reviews
# ============================================================

@app.route('/events/<int:event_id>/reviews')
def event_reviews(event_id):
    """
    Anyone can read the reviews for an event.
    Reviews are ordered newest-first.
    """
    event = Event.query.get_or_404(event_id)
    reviews = Review.query.filter_by(event_id=event_id)\
                          .order_by(Review.created_at.desc())\
                          .all()

    # Calculate average rating for display
    avg_rating = None
    if reviews:
        avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1)

    return render_template(
        'event_reviews.html',
        event=event,
        reviews=reviews,
        avg_rating=avg_rating
    )
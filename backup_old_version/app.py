from flask import Flask, render_template, redirect, url_for, flash, request
from config import Config
from models import db, Event, Registration, HourLog
from forms import RegistrationForm, HourLogForm, EventForm
from datetime import datetime, date, time

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    
    # HOME ROUTE
    @app.route('/')
    def home():
        return render_template('home.html')
    
    # EVENT ROUTES
    @app.route('/events')
    def events():
        all_events = Event.query.all()
        return render_template('events.html', events=all_events)
    
    @app.route('/events/add', methods=['GET', 'POST'])
    def add_event():
        form = EventForm()
        
        if form.validate_on_submit():
            # Combine date and time into datetime
            event_datetime = None
            if form.date.data and form.time.data:
                event_datetime = datetime.combine(form.date.data, form.time.data)
            
            new_event = Event(
                title=form.title.data,
                description=form.description.data,
                date=event_datetime,
                location=form.location.data,
                max_participants=form.max_participants.data or 0
            )
            
            db.session.add(new_event)
            db.session.commit()
            
            flash('Event created successfully!', 'success')
            return redirect(url_for('events'))
        
        return render_template('add_event.html', form=form)
    
    @app.route('/events/delete/<int:id>', methods=['POST'])
    def delete_event(id):
        event = Event.query.get_or_404(id)
        db.session.delete(event)
        db.session.commit()
        flash('Event deleted successfully!', 'success')
        return redirect(url_for('events'))
    
    # REGISTRATION ROUTES
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegistrationForm()
        form.event_id.choices = [(e.id, f"{e.title} - {e.location}") for e in Event.query.all()]
        
        if form.validate_on_submit():
            new_registration = Registration(
                student_name=form.student_name.data,
                event_id=form.event_id.data,
                registration_date=datetime.utcnow()
            )
            
            db.session.add(new_registration)
            db.session.commit()
            
            flash(f'Successfully registered {form.student_name.data}!', 'success')
            return redirect(url_for('events'))
        
        return render_template('register.html', form=form)
    
    @app.route('/registrations')
    def registrations():
        all_registrations = Registration.query.all()
        return render_template('registrations.html', registrations=all_registrations)
    
    # HOUR LOG ROUTES
    @app.route('/log-hours', methods=['GET', 'POST'])
    def log_hours():
        form = HourLogForm()
        form.event_id.choices = [(e.id, e.title) for e in Event.query.all()]
        
        if form.validate_on_submit():
            new_log = HourLog(
                student_name=form.student_name.data,
                event_id=form.event_id.data,
                hours=form.hours.data,
                description=form.description.data,
                submission_date=datetime.utcnow()
            )
            
            db.session.add(new_log)
            db.session.commit()
            
            flash(f'Logged {form.hours.data} hours successfully!', 'success')
            return redirect(url_for('hours_list'))
        
        return render_template('log_hours.html', form=form)
    
    @app.route('/hours')
    def hours_list():
        all_hours = HourLog.query.all()
        return render_template('hours_list.html', hours=all_hours)
    
    # DATABASE SETUP
    with app.app_context():
        db.create_all()
        
        # Add sample data if empty
        if not Event.query.first():
            print("Adding sample events...")
            sample_events = [
                Event(
                    title="Community Garden Cleanup",
                    description="Help clean up the local community garden",
                    date=datetime(2026, 3, 15, 9, 0),
                    location="Durban Community Garden",
                    max_participants=20
                ),
                Event(
                    title="Beach Cleanup Drive",
                    description="Help keep our beaches clean and safe",
                    date=datetime(2026, 3, 20, 8, 0),
                    location="Durban North Beach",
                    max_participants=50
                ),
                Event(
                    title="Food Bank Assistance",
                    description="Sort and pack food donations for distribution",
                    date=datetime(2026, 3, 22, 10, 0),
                    location="Durban Food Bank",
                    max_participants=15
                )
            ]
            for event in sample_events:
                db.session.add(event)
            db.session.commit()
            print("Sample events added!")
    
    return app

app = create_app()

if __name__ == '__main__':
    print("Starting Flask development server...")
    print("Open your browser and go to: http://127.0.0.1:5000")
    app.run(debug=True)
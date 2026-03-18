from flask import Flask, render_template, redirect, url_for, flash, session, request
from functools import wraps
from datetime import datetime

from config import Config
from models import db, User, Event, Registration, HourLog, Notification, Certificate
from forms import RegisterForm, LoginForm, HourLogForm, ReviewHourLogForm, AlertForm, EventForm


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first.', 'warning')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function

    def student_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first.', 'warning')
                return redirect(url_for('login'))
            if session.get('role') != 'student':
                flash('Student access only.', 'danger')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function

    def supervisor_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first.', 'warning')
                return redirect(url_for('login'))
            if session.get('role') != 'supervisor':
                flash('Supervisor access only.', 'danger')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function

    def admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first.', 'warning')
                return redirect(url_for('login'))
            if session.get('role') != 'admin':
                flash('Admin access only.', 'danger')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function

    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm()

        if form.validate_on_submit():
            existing_email_input = form.email.data.strip()
            user = User.query.filter_by(email=email_input).first()
            if existing_user:
                flash('An account with that email already exists.', 'danger')
                return redirect(url_for('register'))

            user = User(
                full_name=form.full_name.data,
                email=form.email.data,
                role=form.role.data
            )
            user.set_password(form.password.data)

            db.session.add(user)
            db.session.commit()

            flash('Account created successfully. Please log in.', 'success')
            return redirect(url_for('login'))

        return render_template('register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            email_input = form.email.data.strip()
            user = User.query.filter_by(email=email_input).first()

            if user and user.check_password(form.password.data):
                session['user_id'] = user.id
                session['role'] = user.role
                session['full_name'] = user.full_name

                if user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                if user.role == 'supervisor':
                    return redirect(url_for('supervisor_dashboard'))
                return redirect(url_for('student_dashboard'))

            flash('Invalid email or password.', 'danger')



        return render_template('login.html', form=form)

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Logged out successfully.', 'success')
        return redirect(url_for('home'))

    @app.route('/student/dashboard')
    @student_required
    def student_dashboard():
        student_id = session['user_id']
        registrations = Registration.query.filter_by(student_id=student_id).all()
        logs = HourLog.query.filter_by(student_id=student_id).all()
        notifications = Notification.query.filter_by(user_id=student_id).order_by(Notification.created_at.desc()).all()
        return render_template('student_dashboard.html', registrations=registrations, logs=logs, notifications=notifications)

    @app.route('/student/events')
    @student_required
    def student_events():
        student_id = session['user_id']
        events = Event.query.filter(Event.status != 'archived').order_by(Event.date.asc()).all()
        registered_event_ids = {r.event_id for r in Registration.query.filter_by(student_id=student_id).all()}
        return render_template('student_events.html', events=events, registered_event_ids=registered_event_ids)

    @app.route('/student/events/<int:event_id>/register', methods=['POST'])
    @student_required
    def register_for_event(event_id):
        student_id = session['user_id']
        event = Event.query.get_or_404(event_id)

        if getattr(event, 'status', 'open') != 'open':
            flash('This event is not open for registration.', 'warning')
            return redirect(url_for('student_events'))

        existing = Registration.query.filter_by(student_id=student_id, event_id=event_id).first()
        if existing:
            flash('You are already registered for this event.', 'warning')
            return redirect(url_for('student_events'))

        registration = Registration(student_id=student_id, event_id=event_id)
        db.session.add(registration)
        db.session.commit()

        flash('You have registered for the event successfully.', 'success')
        return redirect(url_for('student_dashboard'))

    @app.route('/student/events/<int:event_id>/log-hours', methods=['GET', 'POST'])
    @student_required
    def log_hours(event_id):
        student_id = session['user_id']
        form = HourLogForm()

        registration = Registration.query.filter_by(student_id=student_id, event_id=event_id).first()
        if not registration:
            flash('You can only log hours for events you registered for.', 'danger')
            return redirect(url_for('student_dashboard'))

        existing_log = HourLog.query.filter_by(student_id=student_id, event_id=event_id).first()
        if existing_log:
            flash('You have already logged hours for this event.', 'warning')
            return redirect(url_for('student_dashboard'))

        event = Event.query.get_or_404(event_id)

        if form.validate_on_submit():
            new_log = HourLog(
                student_id=student_id,
                event_id=event_id,
                hours=form.hours.data,
                description=form.description.data,
                status='pending'
            )
            db.session.add(new_log)
            db.session.commit()

            flash('Your volunteer hours were submitted and are waiting for review.', 'success')
            return redirect(url_for('student_dashboard'))

        return render_template('log_hours.html', form=form, event=event)

    @app.route('/supervisor/dashboard')
    @supervisor_required
    def supervisor_dashboard():
        supervisor_id = session['user_id']
        events = Event.query.filter_by(supervisor_id=supervisor_id).all()

        pending_logs = (
            HourLog.query
            .join(Event, HourLog.event_id == Event.id)
            .filter(Event.supervisor_id == supervisor_id, HourLog.status == 'pending')
            .order_by(HourLog.submitted_at.desc())
            .all()
        )

        reviewed_logs = (
            HourLog.query
            .join(Event, HourLog.event_id == Event.id)
            .filter(Event.supervisor_id == supervisor_id, HourLog.status.in_(['approved', 'rejected']))
            .order_by(HourLog.reviewed_at.desc())
            .all()
        )

        return render_template('supervisor_dashboard.html', events=events, pending_logs=pending_logs, reviewed_logs=reviewed_logs)

    @app.route('/supervisor/logs/<int:log_id>/review', methods=['GET', 'POST'])
    @supervisor_required
    def review_hour_log(log_id):
        form = ReviewHourLogForm()
        log = HourLog.query.get_or_404(log_id)

        if log.event.supervisor_id != session['user_id']:
            flash('You are not allowed to review this log.', 'danger')
            return redirect(url_for('supervisor_dashboard'))

        if form.validate_on_submit():
            log.status = form.status.data
            log.supervisor_comment = form.supervisor_comment.data
            log.reviewed_by = session['user_id']
            log.reviewed_at = datetime.utcnow()

            notification = Notification(
                user_id=log.student_id,
                title='Volunteer Hours Review Update',
                message=f'Your hour log for {log.event.title} was {log.status}. Comment: {log.supervisor_comment or 'No comment provided.'}'
            )

            db.session.add(notification)
            db.session.commit()

            flash('Volunteer hours reviewed successfully.', 'success')
            return redirect(url_for('supervisor_dashboard'))

        return render_template('review_hour_log.html', form=form, log=log)

    @app.route('/supervisor/events/<int:event_id>/alerts', methods=['GET', 'POST'])
    @supervisor_required
    def send_event_alert(event_id):
        form = AlertForm()
        event = Event.query.get_or_404(event_id)

        if event.supervisor_id != session['user_id']:
            flash('You are not allowed to send alerts for this event.', 'danger')
            return redirect(url_for('supervisor_dashboard'))

        if form.validate_on_submit():
            registrations = Registration.query.filter_by(event_id=event.id).all()

            for reg in registrations:
                notification = Notification(
                    user_id=reg.student_id,
                    title=form.title.data,
                    message=f'Event: {event.title}\n{form.message.data}'
                )
                db.session.add(notification)

            db.session.commit()
            flash('Alert sent to all registered student volunteers.', 'success')
            return redirect(url_for('supervisor_dashboard'))

        return render_template('send_alert.html', form=form, event=event)

    @app.route('/admin/dashboard')
    @admin_required
    def admin_dashboard():
        total_users = User.query.count()
        total_students = User.query.filter_by(role='student').count()
        total_supervisors = User.query.filter_by(role='supervisor').count()
        total_admins = User.query.filter_by(role='admin').count()
        total_events = Event.query.count()
        open_events = Event.query.filter_by(status='open').count() if hasattr(Event, 'status') else 0
        pending_logs = HourLog.query.filter_by(status='pending').count()
        approved_logs = HourLog.query.filter_by(status='approved').count()
        total_certificates = Certificate.query.count()

        recent_logs = HourLog.query.order_by(HourLog.submitted_at.desc()).limit(10).all()
        recent_events = Event.query.order_by(Event.id.desc()).limit(5).all()
        users = User.query.order_by(User.id.desc()).all()

        return render_template(
            'admin_dashboard.html',
            total_users=total_users,
            total_students=total_students,
            total_supervisors=total_supervisors,
            total_admins=total_admins,
            total_events=total_events,
            open_events=open_events,
            pending_logs=pending_logs,
            approved_logs=approved_logs,
            total_certificates=total_certificates,
            recent_logs=recent_logs,
            recent_events=recent_events,
            users=users
        )

    @app.route('/admin/events/create', methods=['GET', 'POST'])
    @admin_required
    def admin_create_event():
        form = EventForm()

        if form.validate_on_submit():
            # Handle image upload
            image_filename = None
            file = request.files.get('image')
            if file and file.filename:
                allowed = {'png', 'jpg', 'jpeg', 'webp'}
                ext = file.filename.rsplit('.', 1)[-1].lower()
                if ext in allowed:
                    from werkzeug.utils import secure_filename
                    import os
                    filename = secure_filename(file.filename)
                    unique_name = f"{int(datetime.utcnow().timestamp())}_{filename}"
                    save_path = os.path.join(app.root_path, 'static', 'uploads', 'events', unique_name)
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    file.save(save_path)
                    image_filename = unique_name

            # Combine date and time into one datetime
            event_date = datetime.combine(form.date.data, form.time.data)

            event = Event(
                title=form.title.data,
                description=form.description.data,
                date=event_date,
                location=form.location.data,
                max_participants=form.max_participants.data,
                category=form.category.data,
                status=form.status.data,
                image_filename=image_filename
            )

            db.session.add(event)
            db.session.commit()

            flash('Event created successfully!', 'success')
            return redirect(url_for('admin_dashboard'))

        return render_template('admin_create_event.html', form=form)

    @app.route('/admin/logs/<int:log_id>/review', methods=['GET', 'POST'])
    @admin_required
    def admin_review_log(log_id):
        form = ReviewHourLogForm()
        log = HourLog.query.get_or_404(log_id)

        if form.validate_on_submit():
            log.status = form.status.data
            log.supervisor_comment = form.supervisor_comment.data
            log.reviewed_by = session['user_id']
            log.reviewed_at = datetime.utcnow()

            notification = Notification(
                user_id=log.student_id,
                title='Admin Review Update',
                message=f'Your hour log for {log.event.title} was {log.status}. Comment: {log.supervisor_comment or 'No comment provided.'}'
            )

            db.session.add(notification)
            db.session.commit()

            flash('Log reviewed successfully by admin.', 'success')
            return redirect(url_for('admin_dashboard'))

        return render_template('review_hour_log.html', form=form, log=log)

    @app.route('/admin/certificates/issue/<int:student_id>', methods=['POST'])
    @admin_required
    def issue_certificate(student_id):
        student = User.query.get_or_404(student_id)

        total_hours = db.session.query(db.func.sum(HourLog.hours)).filter(
            HourLog.student_id == student_id,
            HourLog.status == 'approved'
        ).scalar() or 0

        certificate = Certificate(student_id=student_id, total_hours=total_hours)
        db.session.add(certificate)

        notification = Notification(
            user_id=student_id,
            title='Certificate Issued',
            message=f'Your volunteering certificate has been issued with {total_hours} approved hours.'
        )
        db.session.add(notification)

        db.session.commit()
        flash('Certificate issued successfully.', 'success')
        return redirect(url_for('admin_dashboard'))

    @app.route('/admin/notify', methods=['GET', 'POST'])
    @admin_required
    def admin_notify():
        form = AlertForm()

        if form.validate_on_submit():
            users = User.query.all()
            for user in users:
                note = Notification(
                    user_id=user.id,
                    title=form.title.data,
                    message=form.message.data
                )
                db.session.add(note)

            db.session.commit()
            flash('Platform notification sent to all users.', 'success')
            return redirect(url_for('admin_dashboard'))

        return render_template('admin_notify.html', form=form)

    with app.app_context():
        db.create_all()

        if not User.query.filter_by(email='admin@dut.ac.za').first():
            admin = User(full_name='Default Admin', email='admin@dut.ac.za', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)

        if not User.query.filter_by(email='supervisor@dut.ac.za').first():
            supervisor = User(full_name='Default Supervisor', email='supervisor@dut.ac.za', role='supervisor')
            supervisor.set_password('super123')
            db.session.add(supervisor)

        db.session.commit()

        supervisor = User.query.filter_by(email='supervisor@dut.ac.za').first()

        if not Event.query.first():
            sample_events = [
                Event(
                    title='Community Garden Cleanup',
                    description='Help clean up the local community garden',
                    date=datetime(2026, 3, 15, 9, 0),
                    location='Durban Community Garden',
                    max_participants=20,
                    category='Community Service',
                    status='open',
                    supervisor_id=supervisor.id if supervisor else None
                ),
                Event(
                    title='Beach Cleanup Drive',
                    description='Help keep our beaches clean and safe',
                    date=datetime(2026, 3, 20, 8, 0),
                    location='Durban North Beach',
                    max_participants=50,
                    category='Environmental',
                    status='open',
                    supervisor_id=supervisor.id if supervisor else None
                )
            ]

            for event in sample_events:
                db.session.add(event)
            db.session.commit()

    return app


app = create_app()

if __name__ == '__main__':
    print('Starting Flask development server...')
    print('Open your browser and go to: http://127.0.0.1:5000')
    app.run(debug=True)








from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # student / supervisor / admin
    department = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    supervised_events = db.relationship('Event', backref='supervisor', lazy=True, foreign_keys='Event.supervisor_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, nullable=True)
    location = db.Column(db.String(200), nullable=True)
    max_participants = db.Column(db.Integer, default=0)
    category = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='open')  # open / closed / archived
    supervisor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    registrations = db.relationship('Registration', backref='event', lazy=True, cascade='all, delete-orphan')
    hour_logs = db.relationship('HourLog', backref='event', lazy=True, cascade='all, delete-orphan')


class Registration(db.Model):
    __tablename__ = 'registrations'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('User', backref='registrations', foreign_keys=[student_id])

    __table_args__ = (
        db.UniqueConstraint('student_id', 'event_id', name='unique_student_event_registration'),
    )


class HourLog(db.Model):
    __tablename__ = 'hour_logs'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    hours = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)

    status = db.Column(db.String(20), default='pending')  # pending / approved / rejected
    supervisor_comment = db.Column(db.Text, nullable=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    student = db.relationship('User', foreign_keys=[student_id], backref='hour_logs')
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])

    __table_args__ = (
        db.UniqueConstraint('student_id', 'event_id', name='unique_student_event_hourlog'),
    )


class Certificate(db.Model):
    __tablename__ = 'certificates'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_hours = db.Column(db.Float, default=0)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('User', backref='certificates')


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='notifications')
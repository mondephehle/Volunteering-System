from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create a new SQLAlchemy instance for models
# This will be initialized with the app in app.py
db = SQLAlchemy()

class Event(db.Model):
    """
    Event model representing volunteer opportunities.
    """
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, nullable=True)
    location = db.Column(db.String(200), nullable=True)
    max_participants = db.Column(db.Integer, default=0)
    
    # Relationships
    registrations = db.relationship('Registration', backref='event', lazy=True)
    hour_logs = db.relationship('HourLog', backref='event', lazy=True)
    
    def __repr__(self):
        return f'<Event {self.title}>'


class Registration(db.Model):
    """
    Registration model linking students to events.
    """
    __tablename__ = 'registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Registration {self.student_name} for {self.event_id}>'


class HourLog(db.Model):
    """
    HourLog model for tracking volunteer hours.
    """
    __tablename__ = 'hour_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    hours = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<HourLog {self.hours} hours by {self.student_name}>'
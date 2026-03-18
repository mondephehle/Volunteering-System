from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    student_number = db.Column(db.String(20), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="student")
    department = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Event(db.Model):
    __tablename__ = "event"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime(timezone=True), nullable=False)
    location = db.Column(db.String(200), nullable=True)
    max_participants = db.Column(db.Integer, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default="open")
    total_event_hours = db.Column(db.Float, nullable=False, default=0.0)
    supervisor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    supervisor = db.relationship("User", foreign_keys=[supervisor_id], backref="supervised_events")


class Registration(db.Model):
    __tablename__ = "registration"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
    registered_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    attendance_status = db.Column(db.String(20), default="registered")

    student = db.relationship("User", foreign_keys=[student_id], backref="registrations")
    event = db.relationship("Event", backref="registrations")

    __table_args__ = (
        db.UniqueConstraint("student_id", "event_id", name="uq_registration_student_event"),
    )


class HourLog(db.Model):
    __tablename__ = "hour_log"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
    hours = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="pending")
    comment = db.Column(db.Text, nullable=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    reviewed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    submitted_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    student = db.relationship("User", foreign_keys=[student_id], backref="hour_logs")
    reviewer = db.relationship("User", foreign_keys=[reviewed_by])
    event = db.relationship("Event", backref="hour_logs")

    __table_args__ = (
        db.UniqueConstraint("student_id", "event_id", name="uq_hourlog_student_event"),
    )


class Certificate(db.Model):
    __tablename__ = "certificate"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False)
    approved_hours = db.Column(db.Float, nullable=False, default=0.0)
    total_event_hours = db.Column(db.Float, nullable=False, default=0.0)
    level = db.Column(db.String(20), nullable=False)
    issued_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    issued_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    file_path = db.Column(db.String(255), nullable=True)

    student = db.relationship("User", foreign_keys=[student_id], backref="certificates")
    issuer = db.relationship("User", foreign_keys=[issued_by])
    event = db.relationship("Event", backref="certificates")

    __table_args__ = (
        db.UniqueConstraint("student_id", "event_id", name="uq_certificate_student_event"),
    )


class Notification(db.Model):
    __tablename__ = "notification"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False, default="Notification")
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", backref="notifications")

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, TextAreaField, FloatField, PasswordField,
    SelectField, SubmitField, IntegerField, DateField, TimeField
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Email, EqualTo


# ── Auth Forms ────────────────────────────────────────────────────────────────

class RegisterForm(FlaskForm):
    """Used by /register and student_register.html"""
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    role = SelectField(
        'Role',
        choices=[('student', 'Student'), ('supervisor', 'Supervisor'), ('admin', 'Admin')],
        validators=[DataRequired()]
    )
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Account')


class StudentRegisterForm(FlaskForm):
    """Used by student_register.html — no role field, always registers as student"""
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Account')


class LoginForm(FlaskForm):
    """Used by login.html and student_login.html"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class ForgotPasswordForm(FlaskForm):
    """Used by forgot_password.html"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Link')


class ResetPasswordForm(FlaskForm):
    """Used by reset_password.html"""
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


# ── Event Form ────────────────────────────────────────────────────────────────

class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(min=3, max=150)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    date = DateField('Event Date', validators=[DataRequired()])
    time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[Optional()])
    total_event_hours = FloatField('Total Event Hours', validators=[Optional(), NumberRange(min=0.5, max=24)])
    location = StringField('Location', validators=[Optional(), Length(max=200)])
    max_participants = IntegerField('Maximum Participants', validators=[Optional(), NumberRange(min=1, max=1000)])
    category = StringField('Category', validators=[Optional(), Length(max=100)])
    status = SelectField(
        'Status',
        choices=[('open', 'Open'), ('closed', 'Closed'), ('archived', 'Archived')],
        validators=[DataRequired()]
    )
    supervisor_id = SelectField('Supervisor', coerce=int, validators=[Optional()])
    supervisor_name = StringField('Supervisor Name', validators=[Optional(), Length(max=120)])
    image = FileField('Event Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only')])
    submit = SubmitField('Save Event')


# ── Hour Log Forms ────────────────────────────────────────────────────────────

class HourLogForm(FlaskForm):
    hours = FloatField('Hours Worked', validators=[DataRequired(), NumberRange(min=0.5, max=24)])
    description = TextAreaField('Work Description', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit Hours')


class ReviewHourLogForm(FlaskForm):
    status = SelectField(
        'Decision',
        choices=[('approved', 'Approve'), ('rejected', 'Reject')],
        validators=[DataRequired()]
    )
    supervisor_comment = TextAreaField('Comment', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit Review')


# ── Verification & Review Forms ───────────────────────────────────────────────

class VerifyAttendanceForm(FlaskForm):
    verification_code = StringField(
        'Verification Code',
        validators=[DataRequired(), Length(min=6, max=10)],
        render_kw={"placeholder": "Enter the code shown by your supervisor"}
    )
    hours = FloatField('Hours Worked', validators=[DataRequired(), NumberRange(min=0.5, max=24)])
    description = TextAreaField('What did you do?', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Verify & Log Hours')


class ReviewForm(FlaskForm):
    rating = SelectField(
        'Rating',
        choices=[
            ('5', '⭐⭐⭐⭐⭐  Excellent'),
            ('4', '⭐⭐⭐⭐  Good'),
            ('3', '⭐⭐⭐  Average'),
            ('2', '⭐⭐  Below Average'),
            ('1', '⭐  Poor'),
        ],
        validators=[DataRequired()]
    )
    body = TextAreaField(
        'Your Review',
        validators=[DataRequired(), Length(min=10, max=1000)],
        render_kw={"placeholder": "Share your experience — what went well, what could improve?"}
    )
    submit = SubmitField('Submit Review')


# ── Alert / Notification Forms ────────────────────────────────────────────────

class AlertForm(FlaskForm):
    title = StringField('Alert Title', validators=[DataRequired(), Length(min=3, max=150)])
    message = TextAreaField('Alert Message', validators=[DataRequired(), Length(min=5, max=500)])
    submit = SubmitField('Send Alert')


class NotifyForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=150)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=5, max=500)])
    submit = SubmitField('Send Notification')
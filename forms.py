from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, PasswordField, SelectField, SubmitField, IntegerField, DateField, TimeField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Email, EqualTo
from flask_wtf.file import FileField, FileAllowed


class RegisterForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    role = SelectField(
        'Role',
        choices=[('student', 'Student'), ('supervisor', 'Supervisor'), ('admin', 'Admin')],
        validators=[DataRequired()]
    )
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    
    # Consent fields (optional by default, will be required for students)
    data_privacy = BooleanField(
        'I agree to the Data Privacy Policy and consent to the use of my personal information for program administration',
        validators=[Optional()]
    )
    liability_waiver = BooleanField(
        'I acknowledge and agree to the Liability Waiver. I assume all risks and will not hold the organization responsible for injuries or damages',
        validators=[Optional()]
    )
    photo_media_consent = BooleanField(
        'I consent to having my photograph and/or video recorded during the program for promotional and educational purposes',
        validators=[Optional()]
    )
    background_check = BooleanField(
        'I consent to a background check as required by the organization',
        validators=[Optional()]
    )
    event_participation = BooleanField(
        'I understand and agree to comply with all event rules and instructions during my participation',
        validators=[Optional()]
    )
    program_consent = BooleanField(
        'I certify that I am at least 18 years old and have read and agree to all terms and conditions of the volunteer program',
        validators=[Optional()]
    )
    
    submit = SubmitField('Create Account')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(min=3, max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


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


class AlertForm(FlaskForm):
    title = StringField('Alert Title', validators=[DataRequired(), Length(min=3, max=150)])
    message = TextAreaField('Alert Message', validators=[DataRequired(), Length(min=5, max=500)])
    submit = SubmitField('Send Alert')


class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(min=3, max=150)])
    description = TextAreaField('Description', validators=[Optional()])
    date = DateField('Event Date', validators=[DataRequired()])
    time = TimeField('Event Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    location = StringField('Location', validators=[Optional(), Length(max=200)])
    max_participants = IntegerField('Maximum Participants', validators=[Optional(), NumberRange(min=1, max=1000)])
    total_event_hours = FloatField('Total Event Hours', validators=[Optional(), NumberRange(min=0.5, max=1000)])
    category = StringField('Category', validators=[Optional(), Length(max=100)])
    status = SelectField(
        'Status',
        choices=[('open', 'Open'), ('closed', 'Closed'), ('archived', 'Archived')],
        validators=[DataRequired()]
    )
    supervisor_id    = SelectField('Supervisor', coerce=int, validators=[Optional()])
    image = FileField('Event Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only')])
    submit = SubmitField('Save Event')


class ForgotPasswordForm(FlaskForm):
    email = StringField(
        'Email Address',
        validators=[DataRequired(), Email(), Length(max=120)]
    )
    submit = SubmitField('Send Reset Link')


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        'New Password',
        validators=[DataRequired(), Length(min=6, message='Password must be at least 6 characters.')]
    )
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match.')]
    )
    submit = SubmitField('Reset Password')


class ConsentForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    
    data_privacy = BooleanField(
        'I agree to the Data Privacy Policy and consent to the use of my personal information for program administration',
        validators=[DataRequired(message='You must agree to the data privacy policy')]
    )
    liability_waiver = BooleanField(
        'I acknowledge and agree to the Liability Waiver. I assume all risks and will not hold the organization responsible for injuries or damages',
        validators=[DataRequired(message='You must agree to the liability waiver')]
    )
    photo_media_consent = BooleanField(
        'I consent to having my photograph and/or video recorded during the program for promotional and educational purposes',
        validators=[DataRequired(message='You must agree to photo/media consent')]
    )
    background_check = BooleanField(
        'I consent to a background check as required by the organization',
        validators=[DataRequired(message='You must agree to the background check')]
    )
    event_participation = BooleanField(
        'I understand and agree to comply with all event rules and instructions during my participation',
        validators=[DataRequired(message='You must agree to event participation terms')]
    )
    program_consent = BooleanField(
        'I certify that I am at least 18 years old and have read and agree to all terms and conditions of the volunteer program',
        validators=[DataRequired(message='You must agree to the program consent')]
    )
    submit = SubmitField('Create Account')
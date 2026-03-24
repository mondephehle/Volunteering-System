from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, PasswordField, SelectField, SubmitField, IntegerField, DateField, TimeField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Email, EqualTo
from flask_wtf.file import FileField, FileAllowed


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from email_validator import validate_email, EmailNotValidError

class RegisterForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=120)])
    
    # Standard email format validation
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    
    role = SelectField(
        'Role',
        choices=[('student', 'Student'), ('supervisor', 'Supervisor'), ('admin', 'Admin')],
        validators=[DataRequired()]
    )
    
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Account')

    def validate_email(self, field):
        """
        Custom validator to enforce Gmail, Outlook, and DUT domains 
        while checking if the email actually exists.
        """
        email_addr = field.data.lower().strip()
        
        # 1. Define the authorized domains for the DUT project
        allowed_domains = [
            'gmail.com', 
            'outlook.com', 
            'hotmail.com', 
            'live.com', 
            'outlook.co.za',
            'dut4life.ac.za'
        ]
        
        # Extract the domain from the email string
        domain = email_addr.split('@')[-1]
        
        # 2. Domain Restriction Check
        if domain not in allowed_domains:
            raise ValidationError('Registration is restricted to Gmail, Outlook, or @dut4life.ac.za accounts.')

        # 3. Deliverability Check
        # This verifies the domain has valid MX records to receive mail
        try:
            validate_email(email_addr, check_deliverability=True)
        except EmailNotValidError:
            raise ValidationError('This email address is not active or cannot receive mail.')


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
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, PasswordField, SelectField, SubmitField, IntegerField, DateField, TimeField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Email, EqualTo


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
    submit = SubmitField('Create Account')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
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
    location = StringField('Location', validators=[Optional(), Length(max=200)])
    max_participants = IntegerField('Maximum Participants', validators=[Optional(), NumberRange(min=1, max=1000)])
    category = StringField('Category', validators=[Optional(), Length(max=100)])
    status = SelectField(
        'Status',
        choices=[('open', 'Open'), ('closed', 'Closed'), ('archived', 'Archived')],
        validators=[DataRequired()]
    )
    submit = SubmitField('Save Event')

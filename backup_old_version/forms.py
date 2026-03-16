from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField, DateField, TimeField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class RegistrationForm(FlaskForm):
    student_name = StringField('Student Name', validators=[DataRequired(), Length(min=2, max=100)])
    event_id = SelectField('Select Event', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Register for Event')


class HourLogForm(FlaskForm):
    student_name = StringField('Student Name', validators=[DataRequired(), Length(min=2, max=100)])
    event_id = SelectField('Select Event', coerce=int, validators=[DataRequired()])
    hours = FloatField('Hours Worked', validators=[DataRequired(), NumberRange(min=0.5, max=24)])
    description = TextAreaField('Work Description', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit Hours')


class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Event Description', validators=[Optional()])
    
    # EASIER DATE/TIME INPUTS
    date = DateField('Event Date', validators=[Optional()])
    time = TimeField('Event Time', validators=[Optional()])
    
    location = StringField('Location', validators=[Optional(), Length(max=200)])
    max_participants = IntegerField('Maximum Participants', validators=[Optional(), NumberRange(min=1, max=1000)])
    submit = SubmitField('Create Event')
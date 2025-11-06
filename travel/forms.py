from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms.fields import TextAreaField, SubmitField, StringField, DateField, TimeField, FloatField, IntegerField, SelectMultipleField, SelectField, PasswordField
from wtforms.validators import InputRequired, Length, NumberRange, DataRequired, ValidationError, email, EqualTo, Regexp
from wtforms.widgets import CheckboxInput, ListWidget

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

def validate_genres(form, field):
    """Custom validator for genres - allows 1 or more but not all"""
    if not field.data or len(field.data) == 0:
        raise ValidationError('Please select at least one genre.')
    if len(field.data) >= 9:  # 9 is the total number of genre options
        raise ValidationError('Please select specific genres, not all of them.')

def validate_event_date(form, field):
    """Custom validator for event date - must be at least 1 day in the future"""
    from datetime import date, timedelta
    
    if field.data:
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        if field.data < tomorrow:
            raise ValidationError('Event date must be at least 1 day in the future.')

class EventForm(FlaskForm):
    name = StringField('Concert Name', validators=[InputRequired(), Length(min=1, max=100)])
    artist = StringField('Artist/Band Name', validators=[InputRequired(), Length(min=1, max=100)])
    overview = TextAreaField('Overview', validators=[InputRequired(), Length(min=1, max=500)])
    location = StringField('Location', validators=[InputRequired(), Length(min=1, max=200)])
    description = TextAreaField('Description', validators=[InputRequired(), Length(min=1, max=2000)])
    
    # Genre selection
    genres = MultiCheckboxField('Genres', choices=[
        ('Pop', 'Pop'),
        ('Punk', 'Punk'),
        ('Rock', 'Rock'),
        ('Jazz', 'Jazz'),
        ('Metal', 'Metal'),
        ('Hip-Hop', 'Hip-Hop'),
        ('Country', 'Country'),
        ('Electronic', 'Electronic'),
        ('Other', 'Other')
    ], validators=[validate_genres])
    
    image = FileField('Concert Image', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg', 'JPG', 'PNG', 'GIF', 'JPEG', 'webp', 'WEBP'], 'Images only!')])
    event_date = DateField('Event Date', validators=[InputRequired(), validate_event_date])
    start_time = TimeField('Start Time', validators=[InputRequired()])
    end_time = TimeField('End Time', validators=[InputRequired()])
    submit = SubmitField("Create Event")

class TicketForm(FlaskForm):
    name = StringField('Ticket Name', validators=[InputRequired(), Length(min=1, max=100)])
    price = FloatField('Price', validators=[InputRequired(), NumberRange(min=0, message='Price must be positive')])
    availability = IntegerField('Availability', validators=[InputRequired(), NumberRange(min=1, message='Availability must be at least 1')])
    description = TextAreaField('Ticket Description', validators=[InputRequired(), Length(min=1, max=500)])
    submit = SubmitField("Add Ticket")


class CommentForm(FlaskForm):
    text = TextAreaField('Comment', validators=[InputRequired(), Length(min=1, max=500)])
    author = StringField('Your Name')  # No validators needed since it's auto-populated
    submit = SubmitField('Submit Comment')

# Legacy forms for backward compatibility
class DestinationForm(FlaskForm):
    name = StringField('Country', validators=[InputRequired()])
    description = TextAreaField('Description', validators=[InputRequired()])
    image = StringField('Cover Image', validators=[InputRequired()])
    currency = StringField('Currency', validators=[InputRequired()])
    submit = SubmitField("Create")

class LoginForm(FlaskForm):
  email = StringField('Email', validators=[InputRequired()])
  password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=50)])
  submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[InputRequired()])
    surname = StringField('Surname', validators=[InputRequired()])
    email = StringField('Email ID', validators=[InputRequired(), email()])
    phone = StringField('Contact Number', validators=[InputRequired()])
    address = StringField('Street Address', validators=[InputRequired()])
    password = StringField('Password', validators=[InputRequired(), Length(min=4, max=50)])
    confirm = PasswordField('Confirm Password', validators=[InputRequired(), Length(min=4, max=50), EqualTo('password')])
    submit = SubmitField('Register now')



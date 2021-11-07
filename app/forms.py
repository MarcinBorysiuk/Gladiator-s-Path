from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from app.models import User, Player


class RegisterForm(FlaskForm):

    def validate_username(self, username_to_check):
        user = User.query.filter_by(name=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists. Please, try another username.')

    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email Adress already exists. Please, try a different Email Address.')

    username = StringField('User Name:', validators=[Length(min=2, max=20), DataRequired()])
    email_address = StringField('Email Address:', validators=[Email(), DataRequired()])
    password1 = PasswordField('Password:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField('Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField('Create Account')


class LoginForm(FlaskForm):

    username = StringField('User Name:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    submit = SubmitField('Log in')


class CreateGladiatorForm(FlaskForm):

    def validate_name(self, name_to_check):
        gladiator = Player.query.filter_by(name=name_to_check.data).first()
        if gladiator:
            raise ValidationError('This Gladiator name already exists. Please, try another name.')

    name = StringField("Gladiator's Name", validators=[Length(min=2, max=20), DataRequired()])
    submit = SubmitField("Let's Start!")

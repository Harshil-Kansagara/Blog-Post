from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog import table
from boto3.dynamodb.conditions import Attr
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=18)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        response = table.scan(
            FilterExpression=Attr('Username').eq(username.data)
        )
        if response['Items']:
            raise ValidationError('That username is taken. Please choose a different one.')
    
    def validate_email(self, email):
        response = table.scan(
            FilterExpression=Attr('Email').eq(email.data)
        )
        if response['Items']:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if current_user.username != username.data:
            response = table.scan(
                FilterExpression=Attr('Username').eq(username.data)
            )
            if response['Items']:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            response = table.scan(
                FilterExpression=Attr('Email').eq(email.data)
            )
            if response['Items']:
                raise ValidationError('That username is taken. Please choose a different one.')
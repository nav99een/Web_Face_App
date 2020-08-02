from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import Length, DataRequired, EqualTo
from app.models import User

class RegistrationForm(FlaskForm):
	login_id = StringField('Login ID', validators=[DataRequired(), Length(min=2, max=20)])
	#email = StringField('Email', validators=[Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign Up')
	def validate_login_id(self,login_id):
		user = User.query.filter_by(login_id=login_id.data).first()
		if user:
			raise ValidationError('This login_id is already taken. Please choose other one.')

class LoginForm(FlaskForm):
	login_id = StringField('Login ID', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	#remember =  BooleanField('Remember Me')
	submit = SubmitField('Login')

class IPLoginForm(FlaskForm):
	ip_address = StringField('IP Address', validators=[DataRequired()])
	port = PasswordField('Port', validators=[DataRequired()])
	#remember =  BooleanField('Remember Me')
	submit = SubmitField('Start')

class UpdateAccountForm(FlaskForm):
	login_id = StringField('Login Id',
		           validators=[DataRequired(), Length(min=2, max=20)])
	#email = StringField('Email',
	#	        validators=[DataRequired(), Email()])
	#picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
	submit = SubmitField('Update')

	def validate_login_id(self, login_id):
		if login_id.data != current_user.login_id:
			user = User.query.filter_by(login_id=login_id.data).first()
			if user:
				raise ValidationError('This login_id is already taken. Please choose a different one.')

	'''def validate_email(self, email):
		if email.data != current_user.email:
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('This email is already taken. Please choose a different one.')'''


class PostForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired()])
	image = FileField('Upload Picture', validators=[DataRequired(), FileAllowed(['jpg','jpeg','png'])])
	submit = SubmitField('Upload')

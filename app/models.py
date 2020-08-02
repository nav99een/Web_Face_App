from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(login_id):
    return User.query.get(int(login_id))


class User(db.Model, UserMixin):
	
	id = db.Column(db.Integer, primary_key=True)
	login_id = db.Column(db.String(20), unique=True, nullable=False)
	#email = db.Column(db.String(120), unique=True, nullable=False)
	#image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
	password = db.Column(db.String(60), nullable=False)
	ip_address = db.Column(db.String(60), nullable=False, default='192.168.43.1')
	port = db.Column(db.String(60), nullable=False, default='8000')
	databases = db.relationship('DataBase', backref='logid', lazy=True)

	def __repr__(self):
		return f"User('{self.login_id}')"

class DataBase(db.Model):
	
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20), nullable=False)
	image = db.Column(db.String(20), nullable=False)
	enc = db.Column(db.String(10000))
	isPresent = db.Column(db.Integer)
	db_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	date_posted = db.Column(db.DateTime, default=datetime.utcnow)

	#encoding = db.relationship('Encoding', backref='id', lazy=True)
	def face_encoding(self):
		if(self.enc is not None):
			return [float(x) for x in self.enc.split(';')[:-1]]
		return []

	def __repr__(self):
		return f"DataBase('{self.name}', '{self.image}')"

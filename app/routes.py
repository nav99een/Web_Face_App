import os
import secrets
from PIL import Image
from app import app, db, bcrypt
from app.models import User, DataBase
from flask import render_template, url_for, redirect, flash, request, abort, Response
from app.flask_forms import (RegistrationForm, LoginForm, PostForm, IPLoginForm)
from flask_login import UserMixin
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
import cv2
from app.camera import VideoCamera
import face_recognition


@app.route("/")
@app.route('/login', methods = ['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('Home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(login_id=form.login_id.data).first()
		if user and (user.password==form.password.data):
		    login_user(user)
		    next_page = request.args.get('next')
		    return redirect(next_page) if next_page else redirect(url_for('Home'))
		else:
		    flash('Login Unsuccessful. Please check login_id and password', 'danger')
	return render_template('login.html', title='Login', form=form)



@app.route('/home')
def Home():
	page = request.args.get('page', 1, type=int)
	posts = DataBase.query.filter_by(db_id=current_user.id)
	posts = posts.order_by(DataBase.date_posted.desc()).paginate(page=page, per_page=10)
	#present = DataBase.query.filter_by(isPresent=1)
	return render_template('home.html', posts=posts)#, present=present)


@app.route('/register', methods = ['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('Home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		password = form.password.data
		user = User(login_id=form.login_id.data,password=password)
		db.session.add(user)
		db.session.commit()
		flash(f'Your account has been created.', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)



@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = app.config['UPLOAD_FOLDER']+picture_fn

	output_size = (300, 300)
	i = Image.open(form_picture)
	i = i.resize(output_size)
	i.save(picture_path)
	img = cv2.imread(picture_path)
	face_encoding = face_recognition.face_encodings(img)[0]
	enc = ''
	for i in face_encoding:
		enc += str(i)+';'
	return picture_fn, enc

'''@app.route("/account", methods = ['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	return render_template('account.html', title='Account',
			   image_file=image_file, form=form)'''


@app.route("/upload", methods = ['GET', 'POST'])
@login_required
def new_data():
	form = PostForm()
	#present = DataBase.query.filter_by(isPresent=1)
	if form.validate_on_submit():
		image_file, enc = save_picture(form.image.data)
		data = DataBase(name=form.name.data, image=image_file, logid=current_user, enc=enc)
		db.session.add(data)
		db.session.commit()
		flash('Your post has been created!', 'success')
		return redirect(url_for('Home'))
	return render_template('create_data.html', title='New Post',
                           form=form, legend='New Post')


'''@app.route("/post/<int:post_id>/update", methods = ['GET', 'POST'])
def update_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.content.data
		db.session.commit()
		flash('Your post has been updated!', 'success')
		return redirect(url_for('post', post_id=post.id))
	elif request.method == 'GET':
		form.title.data = post.title
		form.content.data = post.content
	return render_template('create_post.html', title='Update Post',
		           form=form, legend='Update Post')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash('Your post has been deleted!', 'success')
	return redirect(url_for('Home'))


@app.route("/user/<string:username>")
def user_posts(username):
	page = request.args.get('page', 1, type=int)
	user = User.query.filter_by(username=username).first_or_404()
	posts = Post.query.filter_by(author=user)\
		.order_by(Post.date_posted.desc())\
		.paginate(page=page, per_page=5)
	return render_template('user_posts.html', posts=posts, user=user)



@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('Home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash('An email has been sent with instructions to reset your password.', 'info')
		return redirect(url_for('login'))
	return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('Home'))
	user = User.verify_reset_token(token)
	if user is None:
		flash('That is an invalid or expired token', 'warning')
		return redirect(url_for('reset_request'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash('Your password has been updated! You are now able to log in', 'success')
		return redirect(url_for('login'))
	return render_template('reset_token.html', title='Reset Password', form=form)'''

@login_required
def get_credentials():
	log_id = current_user.login_id
	pwd = current_user.password
	ip_add = current_user.ip_address
	port = current_user.port
	return str(log_id)+':'+str(pwd)+'@'+str(ip_add)+':'+str(port)

def gen(camera):
    while True:
        #get camera frame
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@login_required
@app.route('/ip_login', methods = ['GET', 'POST'])
def ip_login():
	form = IPLoginForm()
	#present = DataBase.query.filter_by(isPresent=1)
	if form.validate_on_submit():
		if form.ip_address.data:
			current_user.ip_address = form.ip_address.data
			current_user.port = form.port.data
			db.session.commit()
			return redirect(url_for('vid'))
	return render_template('ip_login.html', title='IP-Login', form=form)#, present=present)


@app.route("/internet")
def vid():
	#present = DataBase.query.filter_by(isPresent=1)
	return render_template('video_ip.html')#, present=present)


@login_required
@app.route("/ip_camera")
def ip_camera():
	url = 'http://'+get_credentials()+'/video'
	return Response(gen(VideoCamera(url)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/web_camera")
def vid1():
	return render_template('video_web.html')

@login_required
@app.route('/video_feed')
def video_feed():
	url = 0
	return Response(gen(VideoCamera(url)),mimetype='multipart/x-mixed-replace; boundary=frame')







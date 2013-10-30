"""
	Main coding for the CNS web application that polls touring students for their information.
	
	Copyright (c) 2013 Robert MacGregor
"""
import os
from datetime import date

from settings import Settings

import bcrypt
from flask import Flask, render_template, request, session
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder='static', static_url_path='/content')
work_factor = 10
db = SQLAlchemy(app)
# Only one Admin user so we don't need to track any other logins.
app.session_token = os.urandom(24)

class Student(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(32))
	last_name = db.Column(db.String(32))
	email = db.Column(db.String(32))
	homephone = db.Column(db.String(32))
	cellphone = db.Column(db.String(32))
	district = db.Column(db.String(32))
	city = db.Column(db.String(32))
	street = db.Column(db.String(32))
	zip = db.Column(db.Integer)
	grade = db.Column(db.Integer)
	year = db.Column(db.Integer)

	date = db.Column(db.String(32))
	
	def __init__(self, first_name, last_name, email, homephone, cellphone, district, city, street, zip, grade, year):
		self.first_name = first_name
		self.last_name = last_name
		self.email = email
		self.homephone = homephone
		self.cellphone = cellphone
		self.district = district
		self.city = city
		self.street = street
		self.zip = zip
		self.grade = grade
		self.year = year

		self.date = '1/15/95'
		
	def __repr__(self):
		return '<Student %s>' % (self.first_name)
		
class Administrator(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(32), unique=True)
	name = db.Column(db.String(64), unique=True)
	hash = db.Column(db.String(128), unique=True)
	
	def __init__(self, name, username, password):
		self.username = username.lower()
		self.hash = bcrypt.hashpw(password, bcrypt.gensalt(work_factor))
		self.name = name

	def test_password(self, password):
		if (bcrypt.hashpw(password, self.hash) == self.hash):
			return True
		return False

	def set_password(self, password):
		self.hash = self.hash = bcrypt.hashpw(password, bcrypt.gensalt(work_factor))
	
	def __repr__(self):
		return '<Administrator %s,%s,%s>' % (self.username, self.name, self.hash)

def get_schools(select=True):
	if (select):
		listing = [ 'Select' ]
	else:
		listing = [ ]
	with open('schools.txt') as handle:
		for line in handle:
			listing.append(line.strip("\r\n"))
	return listing
	
class ApplicationException(Exception):
	""" This is an exception used internally to help make the code cleaner. """
				
@app.route("/")
def main():
	return render_template('index.html')

@app.route("/changeconfig", methods=["POST"])
def changeconfig():
	token = None
	if ('token' in session):
		token = session['token']

	if (token is None or token != app.session_token):
		return 'You are not logged in.'

	account = db.session.query(Administrator).first()

	realname = request.form["realname"]
	username = request.form["username"]
	current_password = request.form["currentpassword"]

	if (not account.test_password(current_password)):
		return render_template('config.html', realname=realname, username=username, error='That is not the current password for this account.')

	new_password = request.form["password"]
	confirm_password = request.form["confirmpassword"]

	if (new_password != confirm_password):
		return render_template('config.html', realname=realname, username=username, error='The new passwords do not match.')

	account.name = realname
	account.username = username.lower()
	account.set_password(confirm_password)
	db.session.add(account)
	db.session.commit()

	return render_template('panel.html', name=realname)

@app.route("/config")
def config():
	token = None
	if ('token' in session):
		token = session['token']

	if (token is None or token != app.session_token):
		return 'You are not logged in.'

	account = db.session.query(Administrator).first()
	return render_template('config.html', username=account.username, realname=account.name)

@app.route("/logout")
def logout():
	token = None
	if ('token' in session):
		token = session['token']

	if (token is None or token != app.session_token):
		return 'You are not logged in.'

	app.session_token = os.urandom(24)
	return render_template('login.html')

@app.route("/search", methods=["POST","GET"])
def search():
	token = None
	if ('token' in session):
		token = session['token']

	if (token is None or token != app.session_token):
		return 'You are not logged in.'

	years = [ ]
	students = db.session.query(Student)
	for student in students:
		if (student.year not in years):
			years.append(student.year)

	if (request.method == "POST"):
		year = int(request.form["year"])
		results = db.session.query(Student).filter_by(year=year)
		return render_template('search.html', years=years, results=results, year=year)

	return render_template('search.html', years=years)

@app.route("/download/<year>")
def download(year):
	token = None
	if ('token' in session):
		token = session['token']

	if (token is None or token != app.session_token):
		return 'You are not logged in.'

	year = int(year)
	students = db.session.query(Student).filter_by(year=year)
	return render_template('download.html', students=students)

@app.route("/admin", methods=["POST","GET"])
def admin():
	token = None
	if ('token' in session):
		token = session['token']

	if (request.method == "GET" and (token is None or token != app.session_token)):
		return render_template('login.html')

	account = db.session.query(Administrator).first()
	if (request.method == "GET" and token is not None and token == app.session_token):
		return render_template('panel.html', name=account.name)
	else:
		username = request.form["username"].lower()
		password = request.form["password"]

		if (account.username != username or account.test_password(password) is not True):
			return render_template('login.html', error='Invalid username or password.')

		token = os.urandom(24)
		app.session_token = token
		session['token'] = token

		if (account.username == 'Default' or account.name == 'Default'):
			return render_template('panel.html', name=account.name, warning='It appears you need to change your account defaults.')
		else:
			return render_template('panel.html', name=account.name)

@app.route("/form", methods=["POST","GET"])
def form():
	if (request.method == "POST"):
		firstname = request.form["firstname"]
		lastname = request.form["lastname"]
		street = request.form["street"]
		homephone = request.form["homephone"]
		cellphone = request.form["cellphone"]

		if (homephone == ''):
			homephone = cellphone
		if (cellphone == ''):
			cellphone = homephone

		city = request.form["city"]
		zip = request.form["zip"]
		email = request.form["email"]
		school = request.form["school"]
		
		error_number = 0
		"""
			0 = Good
			1 = Bad Home Phone
			2 = Bad Cell Phone
			3 = Bad ZIP
			4 = Bad EMail
			5 = Bad School
			6 = Bad Grade
		"""
		
		schools = get_schools(select=False)
		
		try:
			# Check if the selected grade is valid.
			grade = request.form["grade"]
			try:
				grade_test = int(grade)
				if (grade_test < 9 or grade_test > 12):
					raise ApplicationException(6)
			except ValueError:
				raise ApplicationException(6)
			
			# Check if the ZIP code is valid.
			zip = request.form["zip"]
			try:
				zip_test = int(zip)
				zip_length = len(zip)
				if (zip_length != 5):
					raise ApplicationException(3)
			except ValueError:
				raise ApplicationException(3)
				
			# Check if the school is valid
			if (school not in schools):
				raise ApplicationException(5)
				
			# E-Mails should contain a single @ symbol
			if (email.count('@') != 1):
				raise ApplicationException(4)
			email = email.strip('@').lower()

			# Check if the home phone is valid
			homephone = str(homephone).translate(None, '(.-) ')
			if (homephone == ''): homephone = '0'
			cellphone = str(cellphone).translate(None, '(.-) ')
			if (cellphone == ''): cellphone = '0'
			
			try:
				homephone_test = int(homephone)
				if (len(homephone) != 10 and len(cellphone) == 1):
					raise ApplicationException(1)
			except ValueError:
				raise ApplicationException(1)
			
			# Check if the cell phone is valid
			try:
				cellphone_test = int(cellphone)
				if (len(cellphone) != 10 and len(homephone) == 1):
					raise ApplicationException(2)
			except ValueError:
				raise ApplicationException(2)

		except ApplicationException as e:
			error_number = int(str(e))

		# TODO: Perhaps make this some type of switch construct at some point?
		if (error_number == 0): # No Problem
			today = date.today()
			student = Student(firstname, lastname, email, homephone, cellphone, school, city, street, int(zip), int(grade), today.year)
			db.session.add(student)
			db.session.commit()
			return render_template('index.html')
		elif (error_number == 1): # Bad Phone number
			return render_template('form.html', title='CNS - Error', error='Please type in either phone number.', firstname=firstname,
									lastname=lastname, street=street, cellphone=cellphone, city=city, zip=zip, email=email, 
									schools=schools)
		elif (error_number == 2): # Bad Cell Phone
			return render_template('form.html', title='CNS - Error', error='Please type in either phone number.', firstname=firstname,
									lastname=lastname, street=street, homephone=homephone, city=city, zip=zip, email=email, schools=schools)
		elif (error_number == 3): # Bad ZIP
			return render_template('form.html', title='CNS - Error', error='Malformed ZIP code detected.', firstname=firstname,
									lastname=lastname, street=street, homephone=homephone, city=city, email=email, schools=schools)
		elif (error_number == 4): # Bad Email
			return render_template('form.html', title='CNS - Error', error='Malformed E-Mail detected.', firstname=firstname,
									lastname=lastname, street=street, homephone=homephone, city=city, zip=zip, email=email, schools=schools)
		elif (error_number == 5): # Bad School (Woodland Hills)
			schools.insert(0, "Select")
			return render_template('form.html', title='CNS - Error', error='Invalid school selected: ' + school, firstname=firstname,
									lastname=lastname, street=street, homephone=homephone, city=city, zip=zip, email=email, schools=schools)
		elif (error_number == 6): # Bad Grade
			return render_template('form.html', title='CNS - Error', error='Invalid grade selected.', firstname=firstname,
									lastname=lastname, street=street, homephone=homephone, city=city, zip=zip, email=email, schools=schools)
	else:
		return render_template('form.html', title='CNS', schools=get_schools(select=True))

if __name__ == "__main__":
	settings = Settings('config.cfg')

	app.config['SQLALCHEMY_DATABASE_URI'] = settings.get_index('DatabaseURI', str)
	app.secret_key = settings.get_index('SecretKey', str)
	work_factor = settings.get_index('WorkFactor', int)
	app.run(debug=True,host='127.0.0.1')

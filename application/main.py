"""
	Main coding for the CNS web application that polls touring students for their information.
	
	Copyright (c) 2013 Robert MacGregor
"""
from flask import Flask, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__, static_folder='static', static_url_path='/content')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://localhost'
db = SQLAlchemy(app)

class Student(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(32), unique=True)
	last_name = db.Column(db.String(32), unique=True)
	email = db.Column(db.String(32), unique=True)
	homephone = db.Column(db.String(32), unique=True)
	cellphone = db.Column(db.String(32), unique=True)
	
	def __init__(self, first_name):
		self.first_name = first_name
		
	def __repr__(self):
		return '<Student %s>' % (self.first_name)
		
class Administrator(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(32), unique=True)
	password = db.Column(db.String(128), unique=True)
	
	def __init__(self, name, password):
		self.name = name
		self.password = password # TODO: Hash it
	
	def __repr__(self):
		return '<Administrator %s,%s>' % (self.name, self.password)

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
def form():
	return render_template('index.html')
	
@app.route("/form", methods=["POST","GET"])
def process():
	if (request.method == "POST"):
		firstname = request.form["firstname"]
		lastname = request.form["lastname"]
		street = request.form["street"]
		homephone = request.form["homephone"]
		cellphone = request.form["cellphone"]
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
			try:
				homephone_test = int(homephone)
				if (len(homephone) != 10):
					raise ApplicationException(1)
			except ValueError:
				raise ApplicationException(1)
			
			# Check if the cell phone is valid
			cellphone = str(cellphone).translate(None, '(.-) ')
			try:
				cellphone_test = int(cellphone)
				if (len(cellphone) != 10):
					raise ApplicationException(2)
			except ValueError:
				raise ApplicationException(2)

		except ApplicationException as e:
			error_number = int(str(e))

		# TODO: Perhaps make this some type of switch construct at some point?
		if (error_number == 0): # No Problem
			return render_template('index.html')
		elif (error_number == 1): # Bad Phone number
			return render_template('form.html', title='CNS - Error', error='Malformed home phone number detected.', firstname=firstname,
									lastname=lastname, street=street, cellphone=cellphone, city=city, zip=zip, email=email, 
									schools=schools)
		elif (error_number == 2): # Bad Cell Phone
			return render_template('form.html', title='CNS - Error', error='Malformed cell phone number detected.', firstname=firstname,
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
	app.run(debug=True,host='0.0.0.0')
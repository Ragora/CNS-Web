from flask import Flask, render_template, request

app = Flask(__name__, static_folder='static', static_url_path='/content')

def get_schools(select=True):
	if (select):
		listing = [ 'Select' ]
	else:
		listing = [ ]
	with open('schools.txt') as handle:
		for line in handle:
			listing.append(line)
	return listing
			
@app.route("/")
def form():
	return render_template('index.html', title='CNS', schools=get_schools(select=True))
	
@app.route("/process", methods=["POST"])
def process():
	firstname = request.form["firstname"]
	lastname = request.form["lastname"]
	street = request.form["street"]
	homephone = request.form["homephone"]
	cellphone = request.form["cellphone"]
	city = request.form["city"]
	zip = request.form["zip"]
	email = request.form["email"]
	school = request.form["school"]
	
	schools = get_schools(select=False)
	if (school not in schools):
			schools.insert(0, "Select")
			return render_template('index.html', title='CNS', error='Invalid school selected: ' + school, firstname=firstname,
							lastname=lastname, street=street, homephone=homephone, cellphone=cellphone, city=city,
							zip=zip, email=email, schools=schools)
	
	# E-Mails should contain a single @ symbol
	if (email.count('@') != 1):
		return render_template('index.html', title='CNS', error='Malformed E-Mail address detected.', firstname=firstname,
								lastname=lastname, street=street, homephone=homephone, cellphone=cellphone, city=city,
								zip=zip, email='')
		
	email = email.strip('@').lower()
	return "BLAH"

if __name__ == "__main__":
	app.run(debug=True)
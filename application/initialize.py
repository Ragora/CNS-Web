"""
	Programming that initializes the software for use.
	
	Copyright (c) 2013 Robert MacGregor
"""
from main import db, Administrator

if __name__ == '__main__':
	db.create_all()
	
	main = Administrator('Default', 'ChangeMeNow')
	db.session.add(main)
	db.session.commit()
	print('Database successfully initialized.')
	
	
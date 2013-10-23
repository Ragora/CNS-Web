"""
	Programming that initializes the software for use.
	
	Copyright (c) 2013 Robert MacGregor
"""
import main
from settings import Settings

if __name__ == '__main__':
	settings = Settings('config.cfg')

	main.app.config['SQLALCHEMY_DATABASE_URI'] = settings.get_index('DatabaseURI', str)
	main.app.secret_key = settings.get_index('SecretKey', str)
	main.work_factor = settings.get_index('WorkFactor', int)

	main.db.create_all()
	
	default_admin = main.Administrator('Default', 'Default', 'ChangeMeNow')
	main.db.session.add(default_admin)
	main.db.session.commit()
	print('Database successfully initialized.')
	
	

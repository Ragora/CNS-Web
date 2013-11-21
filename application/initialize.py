"""
	Programming that initializes the software for use.
	
	Copyright (c) 2013 Robert MacGregor
"""
import main
from settings import Settings

if __name__ == '__main__':
	settings = Settings('config.cfg')

	main.work_factor = settings.get_index('WorkFactor', int)

	main.Base.metadata.create_all(bind=main.engine)
	
	default_admin = main.Administrator('Default', 'Default', 'ChangeMeNow')
	main.db.add(default_admin)
	main.db.commit()
	print('Database successfully initialized.')
	
	

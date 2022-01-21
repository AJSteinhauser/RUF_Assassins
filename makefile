run:
	python3 manage.py runserver

runiphone:
	ipconfig getifaddr en0
	python3 manage.py runserver 0.0.0.0:8000

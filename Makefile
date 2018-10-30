requirements:
	pipenv lock -r > requirements.txt
	pipenv lock -dr > requirements_dev.txt

requirements:
	pipenv lock -r > requirements.txt
	pipenv lock -dr > requirements_dev.txt

macos:
	python setup.py py2app  --packages=PyQt5 --packages=pfreader_gui --packages=pfreader --packages=openpyxl

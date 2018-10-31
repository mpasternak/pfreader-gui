all: win macos

requirements:
	pipenv lock -r > requirements.txt
	pipenv lock -dr > requirements_dev.txt

build_ui:
	python setup.py build_ui

clean:
	rm -rf build dist

mac-clean: clean
	rm pfreader*dmg

mac-app:
	python setup.py py2app  --packages=PyQt5 --packages=pfreader_gui --packages=pfreader --packages=openpyxl

mac-dmg:
	hdiutil create -volname pfreader-gui-`python src/pfreader_gui/__version__.py` -srcfolder dist/ -ov -format UDZO pfreader-gui-`python src/pfreader_gui/__version__.py`.dmg

macos: requirements build_ui mac-clean mac-app mac-dmg

win: requirements build_ui clean
	pynsist installer.cfg



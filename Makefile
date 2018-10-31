requirements:
	pipenv lock -r > requirements.txt
	pipenv lock -dr > requirements_dev.txt


mac-clean:
	rm pfreader*dmg
	rm -rf build dist

mac-app:
	python setup.py py2app  --packages=PyQt5 --packages=pfreader_gui --packages=pfreader --packages=openpyxl

mac-dmg:
	hdiutil create -volname pfreader-gui-`python src/pfreader_gui/__version__.py` -srcfolder dist/ -ov -format UDZO pfreader-gui-`python src/pfreader_gui/__version__.py`.dmg

macos: mac-clean mac-app mac-dmg

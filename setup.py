#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyqt_distutils.build_ui import build_ui
from setuptools import setup

cmdclass = {'build_ui': build_ui}

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


def reqs(fn):
    return list([x.strip()
                 for x in open(fn).readlines()
                 if
                 x.strip()
                 and not x.startswith("-")
                 and not x.startswith("\#")])


requirements = reqs("requirements.txt")
test_requirements = reqs("requirements_dev.txt")

kwargs = {}

import sys

if sys.platform == 'darwin':
    kwargs['app'] = ['src/app.py']
    kwargs['setup_requires'] = 'py2app'
    kwargs['options'] = {
        'py2app': {
            'iconfile': 'src/pfreader_gui/pfreader_gui.icns',
            'plist': {'CFBundleShortVersionString':'0.1.0',}
        }
    }

setup(
    name='pfreader-gui',
    version='0.0.4-dev',
    description="GUI for pfeader, a reader for Baxter® PrismaFlex® LOX files written in Python.",
    long_description=readme + '\n\n' + history,
    author="Michał Pasternak",
    author_email='michal.dtz@gmail.com',
    url='https://github.com/mpasternak/pfreader-gui',
    packages=['pfreader_gui', ],
    package_dir={'pfreader_gui': 'src/pfreader_gui'},
    data_files=[],
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='PrismaFlex Baxter Prisma Flex Gambro LOX files CRRT CVVHDF TPE',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    cmdclass=cmdclass,
    **kwargs
)

# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'Jinja2',
    'webassets',
    'cssmin',
    'colander',
    'simplejson',
    'py-bcrypt',
    'WTForms',
    'pytz',
    'Babel',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'pyramid_jinja2',
    'pyramid_webassets',
    'zope.sqlalchemy',
    'waitress',
]

setup(
    name='alpaca',
    version='0.1.0',
    description='Software error aggregator.',
    long_description=README,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author=u'Mikołaj Siedlarek',
    author_email='m.siedlarek@nctz.net',
    url='https://github.com/msiedlarek/alpaca',
    keywords='web wsgi bfg pylons pyramid error aggregation',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='alpaca.tests',
    install_requires=requires,
    entry_points="""\
        [paste.app_factory]
        main = alpaca:main
        [console_scripts]
        alpaca_initialize_database = alpaca.scripts.initialize_database:main
    """,
)

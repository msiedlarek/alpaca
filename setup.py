import os
from setuptools import setup, find_packages

from alpaca import __version__ as alpaca_version


here = os.path.abspath(os.path.dirname(__file__))


requirements = [
    'pyramid',
    'pyramid_zcml',
    'pyramid_layout',
    'pyramid_tm',
    'waitress',
    'zope.component',
    'zope.interface',
    'zope.configuration',
    'zope.sqlalchemy',
    'sqlalchemy',
    'psycopg2',
    'msgpack-python',
    'pbkdf2',
    'pyzmq',
    'tornado',
    'beaker',
    'colander',
    'pytz',
    'deform',
    'deform_bootstrap',
]


setup(
    name='alpaca',
    version=alpaca_version,
    description='Software error aggregator.',
    long_description='',
    classifiers=[
        'Programming Language :: Python 3',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='Mikołaj Siedlarek',
    author_email='m.siedlarek@nctz.net',
    url='https://github.com/msiedlarek/alpaca',
    keywords='web alpaca error exception logging monitoring',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    tests_require=requirements,
    test_suite='alpaca',
    entry_points={
        'paste.app_factory': [
            'frontend = alpaca.frontend:main',
            'monitor = alpaca.monitor:main',
        ],
        'paste.server_runner': [
            'monitor = alpaca.monitor:server',
        ],
        'console_scripts': [
            'alpaca-admin = alpaca.admin:main',
        ],
    }
)

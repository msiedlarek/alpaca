import os
from setuptools import setup, find_packages

from alpaca import __version__ as alpaca_version


here = os.path.abspath(os.path.dirname(__file__))


requirements = [
    'distribute',
    'psycopg2',
    'pytz',
    'pyramid==1.4.3',
    'pyramid_zcml==1.0.0',
    'pyramid_layout==0.8',
    'pyramid_tm==0.7',
    'waitress==0.8.7',
    'zope.component==4.1.0',
    'zope.interface==4.0.5',
    'zope.configuration==4.0.2',
    'zope.sqlalchemy==0.7.3',
    'sqlalchemy==0.8.2',
    'msgpack-python==0.3.0',
    'pbkdf2==1.3',
    'pyzmq==13.1.0',
    'tornado==3.1.1',
    'beaker==1.6.4',
    'colander==1.0b1',
    'deform==0.9.9',
    'deform_bootstrap==0.2.9',
]


setup(
    name='alpaca',
    version=alpaca_version,
    description='Software error aggregator.',
    long_description=open(os.path.join(here, 'README.txt')).read(),
    classifiers=[
        'Programming Language :: Python 3',
        'Environment :: Web Environment',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Operating System :: OS Independent',
        'Topic :: System :: Logging',
        'Topic :: System :: Monitoring',
        'License :: OSI Approved :: Apache Software License',
    ],
    author='Mikołaj Siedlarek',
    author_email='m.siedlarek@nctz.net',
    url='https://github.com/msiedlarek/alpaca',
    keywords='web alpaca error exception logging monitoring',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    tests_require=requirements + [
        'mock==1.0.1',
    ],
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

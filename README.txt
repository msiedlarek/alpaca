alpaca
======

Alpaca is a software error aggregator based on ZeroMQ transport layer.
Multiple reporters (such as https://github.com/msiedlarek/alpaca-django)
publish detected problems to a central monitoring server using flexible
API. Monitoring server (monitor) shares its database with a web
application (frontend), allowing detailed inspection of each problem.

Running
-------

Starting frontend:

    pserve configuration/development.ini --server-name=frontend \
        --app-name=frontend

Starting monitor:

    pserve configuration/development.ini --server-name=monitor \
        --app-name=monitor

Development
-----------

$ vagrant up
$ vagrant ssh
$ alpaca-admin /vagrant/configuration/development.ini createuser -a user@example.com

Testing
-------

$ vagrant up
$ vagrant ssh
$ python setup.py test

License
-------

Copyright 2013 Mikołaj Siedlarek <msiedlarek@nctz.net>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

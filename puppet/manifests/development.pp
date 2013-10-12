node 'dev-alpaca' {

  stage { 'first':
    before => Stage['main'],
  }

  class { 'apt':
    always_apt_update => true,
    stage             => 'first',
  }

  include utilities_service
  include postgresql_service
  include python3_service
  include alpaca_service
  include apache_service

  file_line { 'autocd_codebase':
    path => '/home/vagrant/.bashrc',
    line => 'if [ -d /vagrant ]; then cd /vagrant; fi',
  }
  file_line { 'autoactivate_virtualenv':
    path => '/home/vagrant/.bashrc',
    line => "if [ -f ${alpaca_service::virtualenv_path}/bin/activate ]; then . ${alpaca_service::virtualenv_path}/bin/activate; fi",
  }

}

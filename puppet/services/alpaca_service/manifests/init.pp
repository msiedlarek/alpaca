class alpaca_service {

  require python3_service
  require postgresql_service

  $virtualenv_path = '/home/vagrant/virtualenv'
  $application_path = '/vagrant'
  $configuration_path = "${application_path}/configuration/development.ini"

  $packages = [
    'g++',
    'postgresql-server-dev-all',
  ]

  package { $packages:
    ensure => present,
  }

  exec { 'create_python_virtualenv':
    command   => "/usr/bin/virtualenv --python=python3 ${virtualenv_path}",
    creates   => $virtualenv_path,
    user      => 'vagrant',
    logoutput => 'on_failure',
    require   => Class['python3_service'],
  }

  exec { 'synchronize_application':
    command   => "${virtualenv_path}/bin/python ${application_path}/setup.py develop",
    timeout   => 3600,
    user      => 'vagrant',
    cwd       => $application_path,
    logoutput => 'on_failure',
    require   => [
      Exec['create_python_virtualenv'],
      Package[$packages],
    ],
  }

  exec { 'synchronize_database_schema':
    command   => "${virtualenv_path}/bin/alpaca-admin ${configuration_path} initdb",
    user      => 'vagrant',
    logoutput => 'on_failure',
    require        => [
      Class['postgresql_service'],
      Exec['synchronize_application'],
    ],
  }

  supervisor::service { 'alpaca-monitor':
    ensure          => present,
    command         => "${virtualenv_path}/bin/pserve ${configuration_path} --reload --server-name=monitor --app-name=monitor",
    user            => 'vagrant',
    stopasgroup     => true,
    redirect_stderr => true,
    require         => [
      Exec['synchronize_application'],
    ],
  }

  supervisor::service { 'alpaca-frontend':
    ensure         => present,
    command        => "${virtualenv_path}/bin/pserve ${configuration_path} --reload --server-name=frontend --app-name=frontend",
    user           => 'vagrant',
    stopasgroup     => true,
    redirect_stderr => true,
    require        => [
      Exec['synchronize_application'],
    ],
  }

}

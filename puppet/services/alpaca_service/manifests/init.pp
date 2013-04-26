class alpaca_service {

  $virtualenv_path = "/home/vagrant/virtualenv"
  $application_path = "/vagrant"
  $configuration_path = "${application_path}/configuration/development.ini"

  package { "postgresql-server-dev-all":
    ensure => present,
  }

  exec { "create_python_virtualenv":
    command   => "/usr/bin/virtualenv --python=python3 ${virtualenv_path}",
    creates   => "${virtualenv_path}",
    user      => "vagrant",
    logoutput => "on_failure",
    require   => Class["python_service"],
  }

  exec { "synchronize_application":
    command   => "${virtualenv_path}/bin/python ${application_path}/setup.py develop",
    timeout   => "3600",
    user      => "vagrant",
    cwd       => $application_path,
    logoutput => "on_failure",
    require   => [
      Exec["create_python_virtualenv"],
      Package["postgresql-server-dev-all"],
    ],
  }

  exec { "synchronize_database_schema":
    command   => "${virtualenv_path}/bin/alpaca-admin ${configuration_path} initdb",
    user      => "vagrant",
    logoutput => "on_failure",
    require        => [
      Exec["synchronize_application"],
    ],
  }

  supervisor::service { "alpaca-monitor":
    ensure         => present,
    command        => "${virtualenv_path}/bin/pserve ${configuration_path} --reload --server-name=monitor --app-name=monitor",
    user           => "vagrant",
    retries        => 100,
    require        => [
      Exec["synchronize_application"],
    ],
  }

  supervisor::service { "alpaca-frontend":
    ensure         => present,
    command        => "${virtualenv_path}/bin/pserve ${configuration_path} --reload --server-name=frontend --app-name=frontend",
    user           => "vagrant",
    retries        => 100,
    require        => [
      Exec["synchronize_application"],
    ],
  }

}

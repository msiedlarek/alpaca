class python3_service {

  $packages = [
    'python3',
    'python3-dev',
    'python-virtualenv',
  ]

  package { $packages:
    ensure => present,
  }

}

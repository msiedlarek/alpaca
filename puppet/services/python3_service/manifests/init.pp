class python3_service {

  $packages = [
    'python3',
    'python3-dev',
    'ipython3',
    'python-virtualenv',
  ]

  package { $packages:
    ensure => present,
  }

}

class python_service {

  $python_packages = [
    "python3",
    "python3-dev",
    "ipython3",
    "python-virtualenv",
    "g++",
  ]
  package { $python_packages:
    ensure => present,
  }

}

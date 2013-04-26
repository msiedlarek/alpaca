class utilities_service {

  $utility_packages = [
    "bash-completion",
    "curl",
    "netcat",
    "htop",
    "vim",
    "git",
  ]

  package { $utility_packages:
    ensure => present,
  }

}

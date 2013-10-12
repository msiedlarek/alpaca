class utilities_service {

  $packages = [
    'ack-grep',
    'htop',
    'netcat',
    'telnet',
    'bash-completion',
    'vim-nox',
    'screen',
    'curl',
    'tree',
    'xz-utils',
    'bzip2',
  ]

  package { $packages:
    ensure => present,
  }

}

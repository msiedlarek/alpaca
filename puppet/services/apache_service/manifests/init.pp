class apache_service {

  package { "apache2-mpm-worker":
    ensure => present,
  }

  file { "/etc/apache2/sites-enabled/000-default":
    ensure  => absent,
    notify  => Service["apache2"],
    require => Package["apache2-mpm-worker"],
  }

  file { "/etc/apache2/sites-available/alpaca":
    ensure  => present,
    content => template("apache_service/alpaca.conf"),
    notify  => Service["apache2"],
    require => Package["apache2-mpm-worker"],
  }

  file { "/etc/apache2/sites-enabled/100-alpaca":
    ensure  => link,
    target  => "/etc/apache2/sites-available/alpaca",
    notify  => Service["apache2"],
    require => [
      Package["apache2-mpm-worker"],
      File["/etc/apache2/sites-available/alpaca"],
    ]
  }

  file { "/etc/apache2/mods-enabled/proxy.load":
    ensure  => link,
    target  => "/etc/apache2/mods-available/proxy.load",
    notify  => Service["apache2"],
    require => Package["apache2-mpm-worker"],
  }

  file { "/etc/apache2/mods-enabled/proxy_http.load":
    ensure  => link,
    target  => "/etc/apache2/mods-available/proxy_http.load",
    notify  => Service["apache2"],
    require => Package["apache2-mpm-worker"],
  }

  service { "apache2":
    ensure  => running,
    require => Package["apache2-mpm-worker"],
  }

}

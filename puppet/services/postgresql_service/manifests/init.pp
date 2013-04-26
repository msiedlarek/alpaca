class postgresql_service {

  include postgresql::server

  postgresql::db { "alpaca":
    user     => "alpaca",
    password => "alpaca",
  }

}

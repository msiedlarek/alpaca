class postgresql_service {

  include postgresql::server

  if defined('alpaca_service') {
    postgresql::db { 'alpaca':
      user     => 'alpaca',
      password => 'alpaca',
    }
  }

}

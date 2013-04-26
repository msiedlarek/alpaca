node "dev-alpaca" {

  include utilities_service
  include postgresql_service
  include python_service
  include alpaca_service
  include apache_service

  Class["postgresql_service"] -> Class["alpaca_service"] -> Class["apache_service"]

}

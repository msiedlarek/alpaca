def main(global_configuration, **local_configuration):
    from alpaca.monitor.application import Application
    settings = global_configuration
    settings.update(local_configuration)
    return Application(settings)


def server(application, global_configuration, **local_configuration):
    from alpaca.monitor.server import Server
    settings = global_configuration
    settings.update(local_configuration)
    server = Server(application, settings)
    server.serve()

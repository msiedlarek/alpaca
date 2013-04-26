from zope import interface


class ICommand(interface.Interface):

    help = interface.Attribute("""""")

    def configure_argument_parser(parser):
        pass

    def __call__(arguments):
        pass

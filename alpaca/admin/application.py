import sys
import argparse

from pyramid.paster import get_appsettings, setup_logging

from alpaca.common.persistence.interfaces import IPersistenceManager
from alpaca.common.persistence.persistence_manager import PersistenceManager
from alpaca.common.registry import Registry
from alpaca.admin.interfaces import ICommand


class Application:

    def __init__(self):
        self.registry = Registry()
        self.registry.load_zcml('alpaca.admin:configure.zcml')
        self._parser = argparse.ArgumentParser()
        self._parser.add_argument(
            'settings',
            help="path to INI file with Alpaca's configuration"
        )
        self._command_parsers = self._parser.add_subparsers(title="Commands")
        self._update_commands()

    def run(self, arguments):
        args = self._parser.parse_args(args=arguments[1:])
        self.registry.load_settings(
            get_appsettings(args.settings, name='alpaca_frontend'),
            'alpaca.admin.commands:configure.zcml'
        )
        setup_logging(args.settings)
        self._update_commands()
        self.registry.registerUtility(
            PersistenceManager(self.registry.settings),
            IPersistenceManager
        )
        args = self._parser.parse_args(args=arguments[1:])
        return_code = args._command(self.registry, args)
        if return_code is not None:
            sys.exit(return_code)

    def _update_commands(self):
        for command_name, command in self.registry.getUtilitiesFor(ICommand):
            parser = self._command_parsers.add_parser(
                command_name,
                help=command.help
            )
            command.configure_argument_parser(parser)
            parser.set_defaults(_command=command)

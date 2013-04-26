import sys

from zope.component import getSiteManager
from zope.interface.registry import Components
from zope.configuration.config import ConfigurationMachine
from zope.configuration import xmlconfig


class Registry(Components):

    def load_settings(self, settings, default_zcml):
        component_configuration_path = settings.get(
            'alpaca.component_configuration_path',
            default_zcml
        )
        self.settings = settings
        self.load_zcml(component_configuration_path)

    def load_zcml(self, zcml_asset_specification):
        def _get_site_manager(context=None):
            return self
        if ':' not in zcml_asset_specification:
            import alpaca
            config_package = alpaca
            config_file = zcml_asset_specification
        else:
            package_name, config_file = zcml_asset_specification.split(':')
            __import__(package_name)
            config_package = sys.modules[package_name]
        context = ConfigurationMachine()
        context.package = config_package
        xmlconfig.registerCommonDirectives(context)
        xmlconfig.file(
            config_file,
            package=config_package,
            context=context,
            execute=False
        )
        getSiteManager.sethook(_get_site_manager)
        try:
            context.execute_actions()
        finally:
            getSiteManager.reset()

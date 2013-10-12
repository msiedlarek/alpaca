import logging
import binascii

import transaction
import pytz
import colander
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
import msgpack

from alpaca.common.persistence.interfaces import IPersistenceManager
from alpaca.common.persistence.persistence_manager import PersistenceManager
from alpaca.common.domain.problem import Problem
from alpaca.common.registry import Registry
from alpaca.common.domain.occurrence import Occurrence
from alpaca.common.services.interfaces import (
    IEnvironmentService,
    IProblemService,
)
from alpaca.monitor.protocol import ReportSchema


logger = logging.getLogger(__name__)


class Application:

    _message_encoding = 'utf-8'
    _environment_data_cache_expiration = 10  # seconds

    def __init__(self, settings):
        self.registry = Registry()
        self.registry.load_settings(settings, 'alpaca.monitor:configure.zcml')

        self._persistence_manager = PersistenceManager(
            self.registry.settings
        )
        self.registry.registerUtility(
            self._persistence_manager,
            IPersistenceManager
        )

        self._cache_manager = CacheManager(**parse_cache_config_options({
            'cache.type': 'memory',
        }))
        self._get_environment = self._cache_manager.cache(
            'alpaca.monitor.application.Application._get_environment',
            expire=self._environment_data_cache_expiration
        )(self._get_environment)

        self._environment_service = self.registry.getAdapter(
            self._persistence_manager,
            interface=IEnvironmentService
        )
        self._problem_service = self.registry.getAdapter(
            self._persistence_manager,
            interface=IProblemService
        )

    def __call__(self, message):
        try:
            environment_name = message[0][:-1].decode(self._message_encoding)
        except IndexError:
            logger.error("Invalid message: empty message.")
            return
        except UnicodeDecodeError:
            logger.error("Invalid message: environment decoding error.")
            return
        try:
            report_cstruct = msgpack.unpackb(
                message[1],
                encoding=self._message_encoding
            )
        except IndexError:
            logger.error("Invalid message: missing report message part.")
            return
        except (ValueError, msgpack.UnpackException):
            logger.error("Invalid message: cannot deserialize report.")
            return
        except UnicodeDecodeError:
            logger.error("Invalid message: report decoding error.")
            return
        environment = self._get_environment(environment_name)
        if environment is None:
            logger.warning(
                "Unknown environment: {environment_name}".format(
                    environment_name=environment_name
                )
            )
            return
        try:
            report = ReportSchema().deserialize(report_cstruct)
        except colander.Invalid as error:
            logger.error(
                "Message validation error: {validation_result}".format(
                    validation_result="; ".join((
                        "{field}: {message}".format(
                            field=field,
                            message=message
                        ) for field, message in error.asdict().items()
                    ))
                )
            )
            return
        description = report['message'].split('\n')[0].strip()
        problem = Problem(
            hash=report['hash'],
            description=description,
            occurrence_count=0,
            first_occurrence=report['date'],
            last_occurrence=report['date'],
            tags=[]
        )
        occurrence = Occurrence(
            environment=environment,
            date=report['date'],
            message=report['message'],
            stack_trace=report['stack_trace'],
            environment_data=report['environment_data']
        )
        with transaction.manager:
            self._problem_service.create_or_update_problem(problem)
            self._problem_service.create_occurrence_of_problem(
                occurrence,
                report['hash']
            )
            self._persistence_manager.session.flush()
            occurrence_id = occurrence.id
        with transaction.manager:
            self._problem_service.limit_problem_history(
                report['hash'],
                int(self.registry.settings['alpaca.problem_history_limit'])
            )
        logger.info(
            "Occurrence of {hash} ({description}) in environment"
            " '{environment}' saved (id={id}).".format(
                hash=binascii.hexlify(report['hash']).decode('ascii'),
                description=description,
                environment=environment_name,
                id=occurrence_id,
            )
        )

    def _get_environment(self, name):
        return self._environment_service.get_environment_by_name(name)

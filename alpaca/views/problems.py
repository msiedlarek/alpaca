import colander
import pytz
import sqlalchemy as sql
from sqlalchemy.orm import exc as database_exceptions
from pyramid.view import view_config
from pyramid import httpexceptions
from pyramid.i18n import get_localizer
from pyramid.response import Response

from alpaca.models import DBSession, Environment, Problem, Occurrence
from alpaca.schemas import ProblemTagsSchema
from alpaca.translation import translate as _

@view_config(
    route_name='alpaca.problems.dashboard',
    request_method='GET',
    renderer='alpaca:templates/dashboard.jinja2',
    permission='alpaca.problems.access'
)
def dashboard(request):
    return {}

@view_config(
    route_name='alpaca.problems.environment',
    request_method='GET',
    renderer='alpaca:templates/environment.jinja2',
    permission='alpaca.problems.access'
)
def environment(request):
    environment_name = request.matchdict['environment_name']
    try:
        environment = DBSession.query(
            Environment.id,
            Environment.name
        ).filter(
            Environment.name == environment_name
        ).one()
    except database_exceptions.NoResultFound:
        raise httpexceptions.HTTPNotFound()
    problems = DBSession.query(
        Problem
    ).distinct().join(
        Occurrence
    ).filter(
        Occurrence.problem_id == Problem.id,
        Occurrence.environment_id == environment.id
    ).order_by(
        Problem.last_occurrence
    )
    return {
        'environment': {
            'id': environment.id,
            'name': environment.name,
        },
        'problems': [
            {
                'id': problem.id,
                'description': problem.description,
                'tags': problem.get_split_tags(),
                'last_occurrence': pytz.utc.normalize(pytz.utc.localize(
                    problem.last_occurrence
                )),
                'occurrence_count': problem.occurrence_count,
                'url': request.route_url(
                    'alpaca.problems.problem',
                    problem_id=problem.id
                ),
            }
            for problem in problems
        ],
    }

@view_config(
    route_name='alpaca.problems.problem',
    request_method='GET',
    renderer='alpaca:templates/problem.jinja2',
    permission='alpaca.problems.access'
)
@view_config(
    route_name='alpaca.problems.problem_occurrence',
    request_method='GET',
    renderer='alpaca:templates/problem.jinja2',
    permission='alpaca.problems.access'
)
def problem(request):
    problem_id = int(request.matchdict['problem_id'])
    try:
        problem = DBSession.query(
            Problem,
        ).filter(
            Problem.id == problem_id
        ).one()
    except database_exceptions.NoResultFound:
        raise httpexceptions.HTTPNotFound()

    try:
        occurrence_id = request.matchdict['occurrence_id']
    except KeyError:
        occurrence = DBSession.query(
            Occurrence
        ).filter(
            Occurrence.problem_id == problem.id
        ).order_by(
            sql.desc(Occurrence.date)
        ).first()
    else:
        try:
            occurrence = DBSession.query(
                Occurrence
            ).filter(
                Occurrence.problem_id == problem.id,
                Occurrence.id == occurrence_id
            ).one()
        except database_exceptions.NoResultFound:
            request.session.flash(
                get_localizer(request).translate(_(
                    "Details of the problem occurrence your URL pointed to were"
                    " removed to limit history size. Please investigate the"
                    " problem using latest occurrence data."
                )),
                queue='warning'
            )
            raise httpexceptions.HTTPSeeOther(
                '#'.join((
                    request.route_url(
                        'alpaca.problems.problem',
                        problem_id=problem.id
                    ),
                    'top'
                ))
            )
    affected_environments = DBSession.query(
        Environment.id,
        Environment.name
    ).distinct().join(
        Occurrence
    ).filter(
        Occurrence.problem_id == problem.id
    ).order_by(
        Environment.name
    )
    problem_occurrences = DBSession.query(
        Occurrence.id
    ).filter(
        Occurrence.problem_id == problem.id
    ).order_by(
        sql.desc(Occurrence.date)
    )
    return {
        'problem': {
            'id': problem.id,
            'hash': problem.hash,
            'first_occurrence': pytz.utc.normalize(pytz.utc.localize(
                problem.first_occurrence
            )),
            'last_occurrence': pytz.utc.normalize(pytz.utc.localize(
                problem.last_occurrence
            )),
            'occurrence_count': problem.occurrence_count,
            'tags': problem.get_split_tags(),
            'occurrences': [
                {
                    'id': problem_occurrence.id,
                    'url': request.route_url(
                        'alpaca.problems.problem_occurrence',
                        problem_id=problem.id,
                        occurrence_id=problem_occurrence.id
                    ),
                }
                for problem_occurrence in problem_occurrences
            ],
        },
        'occurrence': {
            'id': occurrence.id,
            'date': pytz.utc.normalize(pytz.utc.localize(occurrence.date)),
            'message': occurrence.message,
            'stack_trace': occurrence.get_normalized_stack_trace(),
            'environment_data': occurrence.get_normalized_environment_data(),
            'environment': {
                'id': occurrence.environment.id,
                'name': occurrence.environment.name,
                'url': request.route_url(
                    'alpaca.problems.environment',
                    environment_name=occurrence.environment.name
                ),
            }
        },
        'affected_environments': [
            {
                'id': environment.id,
                'name': environment.name,
                'url': request.route_url(
                    'alpaca.problems.environment',
                    environment_name=environment.name
                ),
            }
            for environment in affected_environments
        ],
    }

@view_config(
    route_name='alpaca.problems.set_tags',
    request_method='POST',
    permission='alpaca.problems.access'
)
def set_tags(request):
    problem_id = request.matchdict['problem_id']
    try:
        problem = DBSession.query(
            Problem,
        ).filter(
            Problem.id == problem_id
        ).one()
    except database_exceptions.NoResultFound:
        raise httpexceptions.HTTPNotFound()
    tags_cstruct = request.POST.getall('tags[]')
    try:
        tags = ProblemTagsSchema().deserialize(tags_cstruct)
    except colander.Invalid as error:
        raise httpexceptions.HTTPBadRequest('\r\n'.join((
            _("Invalid tags."),
            '\r\n'.join((
                '%s: %s' % (node_name, message)
                for node_name, message in error.asdict().iteritems()
            ))
        )))
    problem.tags = ','.join(tags)
    DBSession.add(problem)
    return Response()

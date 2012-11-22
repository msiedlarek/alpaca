try:
    import cPickle as pickle
except ImportError:
    import pickle

import pytz
import colander
import sqlalchemy as sql
from sqlalchemy.orm import exc as database_exceptions
from pyramid.view import view_config
from pyramid import httpexceptions
from pyramid.response import Response
import simplejson

from alpaca.models import DBSession, Environment, Problem, Occurrence
from alpaca.schemas import ReportSchema

@view_config(
    route_name='alpaca.api.report',
    request_method='POST',
    permission='alpaca.api.access'
)
def report(request):
    if 'Alpaca-Environment' not in request.headers:
        raise httpexceptions.HTTPBadRequest(
            "Missing Alpaca-Environment header."
        )
    try:
        environment = DBSession.query(Environment).filter(
            Environment.name == request.headers['Alpaca-Environment']
        ).one()
    except database_exceptions.NoResultFound:
        raise httpexceptions.HTTPBadRequest(
            "Unknown environment."
        )
    if 'Alpaca-Signature' not in request.headers:
        raise httpexceptions.HTTPBadRequest(
            "Missing Alpaca-Signature header."
        )
    if request.content_type == 'application/x-pickle.python':
        try:
            report_cstruct = pickle.loads(request.body)
        except pickle.UnpicklingError as error:
            raise httpexceptions.HTTPBadRequest(
                "Cannot parse request body: %s" % str(error)
            )
    elif request.content_type == 'application/json':
        try:
            report_cstruct = simplejson.loads(request.body)
        except simplejson.JSONDecodeError as error:
            raise httpexceptions.HTTPBadRequest(
                "Cannot parse request body: %s" % str(error)
            )
    else:
        raise httpexceptions.HTTPBadRequest("Unsupported Content-Type.")
    try:
        report = ReportSchema().deserialize(report_cstruct)
    except colander.Invalid as error:
        raise httpexceptions.HTTPBadRequest('\r\n'.join((
            "Invalid report.",
            '\r\n'.join((
                '%s: %s' % (node_name, message)
                for node_name, message in error.asdict().iteritems()
            ))
        )))
    if report['date'].tzinfo is None:
        report['date'] = pytz.utc.normalize(pytz.utc.localize(
            report['date']
        ))
    else:
        report['date'] = report['date'].astimezone(pytz.utc)
    try:
        problem = DBSession.query(
            Problem,
        ).filter(
            Problem.hash == report['hash']
        ).one()
    except database_exceptions.NoResultFound:
        problem = Problem()
        problem.hash = report['hash']
        problem.occurrence_count = 1
        problem.first_occurrence = report['date'].replace(tzinfo=None)
    else:
        problem.occurrence_count += 1
    finally:
        problem.description = report['message'].split('\n')[0].strip()
        problem.last_occurrence = report['date'].replace(tzinfo=None)
        DBSession.add(problem)
    occurrence = Occurrence()
    occurrence.problem = problem
    occurrence.environment = environment
    occurrence.date = report['date'].replace(tzinfo=None)
    occurrence.message = report['message']
    occurrence.stack_trace = report['stack_trace']
    occurrence.environment_data = report['environment_data']
    DBSession.add(occurrence)
    DBSession.query(
        Occurrence
    ).filter(
        Occurrence.id.in_(
            DBSession.query(
                Occurrence.id
            ).join(
                Problem
            ).filter(
                Occurrence.problem_id == Problem.id,
                Problem.hash == report['hash']
            ).order_by(
                sql.desc(Occurrence.date)
            ).offset(
                30
            ).subquery()
        )
    ).delete(synchronize_session=False)
    # Call `expire_all()` to avoid having inconsistent state after calling
    # `delete()` with `synchronize_session=False`.
    DBSession.expire_all()
    return Response()

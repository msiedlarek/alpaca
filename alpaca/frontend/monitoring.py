import binascii

import colander
import deform
from pyramid import httpexceptions
from pyramid.response import Response

from alpaca.frontend.i18n import translate as _
from alpaca.frontend.forms import CSRFSecuredSchema
from alpaca.common.services.interfaces import (
    IEnvironmentService,
    IProblemService,
)


def dashboard(request):
    return {}


def environment(request):
    environment_service = request.registry.getAdapter(
        request.persistence_manager,
        IEnvironmentService
    )
    problem_service = request.registry.getAdapter(
        request.persistence_manager,
        IProblemService
    )
    environment = environment_service.get_environment_by_name(
        request.matchdict['environment_name']
    )
    if environment is None:
        raise httpexceptions.HTTPNotFound()
    request.layout_manager.layout.current_environment_id = environment.id
    problems = problem_service.get_environment_problems(environment, limit=50)
    return {
        'environment': {
            'id': environment.id,
        },
        'problems': [
            {
                'id': problem.id,
                'description': problem.description,
                'last_occurrence': problem.last_occurrence,
                'tags': problem.tags,
                'occurrence_count': problem.occurrence_count,
                'path': request.route_path(
                    'alpaca.frontend.monitoring.problem',
                    problem_id=problem.id
                ),
            }
            for problem in problems
        ],
    }


def problem(request):
    environment_service = request.registry.getAdapter(
        request.persistence_manager,
        IEnvironmentService
    )
    problem_service = request.registry.getAdapter(
        request.persistence_manager,
        IProblemService
    )
    problem = problem_service.get_problem(int(request.matchdict['problem_id']))
    if problem is None:
        raise httpexceptions.HTTPNotFound()
    affected_environments = environment_service.get_affected_environments(
        problem
    )
    occurrences = problem_service.get_problem_occurrence_ids(problem)
    try:
        occurrence_id = int(request.matchdict['occurrence_id'])
    except KeyError:
        occurrence_id = occurrences[0].id
    occurrence = problem_service.get_occurrence(occurrence_id)
    if occurrence is None:
        request.session.flash(
            _(
                "Details of the problem occurrence your URL pointed to were"
                " probably removed to limit history size. Please investigate"
                " the problem using latest occurrence data."
            ),
            queue='warning'
        )
        return httpexceptions.HTTPSeeOther(
            request.route_url(
                'alpaca.frontend.monitoring.problem',
                problem_id=problem.id
            )
        )
    set_tags_form = deform.Form(
        SetTagsSchema().bind(
            session=request.session
        ),
        buttons=(
            deform.Button(
                name='submit-save-tags',
                title=_("Save tags")
            ),
        ),
        action=request.route_path('alpaca.frontend.monitoring.set_tags'),
        bootstrap_form_style='form-inline'
    )
    set_tags_form.set_appstruct({
        'id': problem.id,
        'tags': ', '.join(problem.tags),
    })
    return {
        'problem': {
            'id': problem.id,
            'hash': binascii.hexlify(problem.hash),
            'affected_environments': [
                {
                    'id': environment.id,
                    'name': environment.name,
                    'path': request.route_path(
                        'alpaca.frontend.monitoring.environment',
                        environment_name=environment.name
                    ),
                }
                for environment in affected_environments
            ],
            'first_occurrence': problem.first_occurrence,
            'last_occurrence': problem.last_occurrence,
            'occurrence_count': problem.occurrence_count,
            'occurrences': [
                {
                    'id': occurrence.id,
                    'path': request.route_path(
                        'alpaca.frontend.monitoring.problem_occurrence',
                        problem_id=problem.id,
                        occurrence_id=occurrence.id
                    ),
                }
                for occurrence in occurrences
            ],
        },
        'occurrence': {
            'id': occurrence.id,
            'date': occurrence.date,
            'environment': {
                'id': occurrence.environment.id,
                'name': occurrence.environment.name,
                'path': request.route_url(
                    'alpaca.frontend.monitoring.environment',
                    environment_name=occurrence.environment.name
                ),
            },
            'message': occurrence.message,
            'stack_trace': occurrence.stack_trace,
            'environment_data': occurrence.environment_data,
        },
        'set_tags_form': set_tags_form,
    }


def set_tags(request):
    set_tags_form = deform.Form(
        SetTagsSchema().bind(
            session=request.session
        )
    )
    try:
        appstruct = set_tags_form.validate(request.POST.items())
    except deform.ValidationFailure:
        raise httpexceptions.HTTPBadRequest()
    problem_service = request.registry.getAdapter(
        request.persistence_manager,
        IProblemService
    )
    problem = problem_service.get_problem(appstruct['id'])
    if problem is None:
        raise httpexceptions.HTTPBadRequest()
    problem_service.set_problem_tags(
        problem,
        list(set((
            tag.strip()
            for tag in appstruct['tags'].replace(',', ' ').split(' ')
            if tag.strip()
        )))
    )
    if 'X-Requested-With' in request.headers:
        return Response()
    request.session.flash(
        _("Problem tags have been successfully set."),
        queue='success'
    )
    return httpexceptions.HTTPSeeOther(
        request.route_url(
            'alpaca.frontend.monitoring.problem',
            problem_id=appstruct['id']
        )
    )


class SetTagsSchema(CSRFSecuredSchema):

    id = colander.SchemaNode(
        colander.Integer(),
        widget=deform.widget.HiddenWidget()
    )
    tags = colander.SchemaNode(
        colander.String(),
        missing=''
    )

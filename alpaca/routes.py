import collections

ROUTES = collections.OrderedDict((
    # problems
    ('alpaca.problems.dashboard', '/'),
    ('alpaca.problems.environment', '/environment/{environment_name}'),
    ('alpaca.problems.problem', '/{problem_id:\d+}'),
    ('alpaca.problems.problem_occurrence', '/{problem_id:\d+}/{occurrence_id:\d+}'),
    ('alpaca.problems.set_tags', '/set_tags/{problem_id:\d+}'),
    # users
    ('alpaca.users.sign_in', '/sign-in'),
    ('alpaca.users.sign_out', '/sign-out'),
    ('alpaca.users.account', '/account'),
    # configuration
    ('alpaca.configuration.configuration', '/configuration'),
    # api
    ('alpaca.api.report', '/api/report'),
))

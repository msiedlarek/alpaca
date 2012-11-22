import colander

def _valid_variables_mapping(node, value):
    if not hasattr(value, 'iteritems'):
        raise colander.Invalid(
            node,
            "Variable list is not a mapping."
        )
    for variable_name, variable_value in value.iteritems():
        if not isinstance(variable_name, basestring):
            raise colander.Invalid(
                node,
                "Variable name is not a string."
            )
        if not variable_name:
            raise colander.Invalid(
                node,
                "Variable is empty."
            )
        if not isinstance(variable_value, basestring):
            raise colander.Invalid(
                node,
                "Variable value is not a string."
            )

def _valid_environment_data(node, value):
    if not hasattr(value, 'iteritems'):
        raise colander.Invalid(node, "Environment data is not a mapping.")
    for header, variables in value.iteritems():
        if not isinstance(header, basestring):
            raise colander.Invalid(node, "Section header is not a string.")
        if not header:
            raise colander.Invalid(node, "Section header is empty.")
        _valid_variables_mapping(node, variables)

def _valid_tag(node, value):
    if ' ' in value or ',' in value:
        raise colander.Invalid(node, "Tag cannot contain spaces or colons.")

class StackTraceFrameContextLinesSchema(colander.SequenceSchema):

    line = colander.SchemaNode(colander.String(), missing='')

class StackTraceFrameSchema(colander.MappingSchema):

    filename = colander.SchemaNode(colander.String())
    line_number = colander.SchemaNode(
        colander.Integer(),
        validator=colander.Range(min=0)
    )
    function = colander.SchemaNode(colander.String())
    pre_context = StackTraceFrameContextLinesSchema()
    context = colander.SchemaNode(colander.String())
    post_context = StackTraceFrameContextLinesSchema()
    variables = colander.SchemaNode(
        colander.Mapping(unknown='preserve'),
        validator=_valid_variables_mapping
    )

class StackTraceSchema(colander.SequenceSchema):

    frame = StackTraceFrameSchema()

class ReportSchema(colander.MappingSchema):

    hash = colander.SchemaNode(colander.String())
    date = colander.SchemaNode(colander.DateTime())
    message = colander.SchemaNode(colander.String())
    stack_trace = StackTraceSchema()
    environment_data = colander.SchemaNode(
        colander.Mapping(unknown='preserve'),
        validator=_valid_environment_data
    )

class ProblemTagsSchema(colander.SequenceSchema):

    tag = colander.SchemaNode(
        colander.String(),
        validator=_valid_tag
    )

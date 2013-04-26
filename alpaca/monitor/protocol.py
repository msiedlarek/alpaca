import binascii

import colander


class HexadecimalBinary:

    def serialize(self, node, appstruct):
        if appstruct is colander.null:
            return colander.null
        if not isinstance(appstruct, bytes):
            raise colander.Invalid(
                node,
                "{} is not bytes".format(repr(appstruct))
            )
        return binascii.hexlify(appstruct)

    def deserialize(self, node, cstruct):
        if cstruct is colander.null:
            return colander.null
        if not isinstance(cstruct, str):
            raise colander.Invalid(
                node,
                "{} is not a string".format(repr(cstruct))
            )
        return binascii.unhexlify(cstruct.encode('ascii'))

    def cstruct_children(self):
        return []


def _valid_variables_mapping(node, value):
    if not hasattr(value, 'items'):
        raise colander.Invalid(
            node,
            "Variable list is not a mapping."
        )
    for variable_name, variable_value in value.items():
        if not isinstance(variable_name, str):
            raise colander.Invalid(
                node,
                "Variable name is not a string."
            )
        if not variable_name:
            raise colander.Invalid(
                node,
                "Variable name is empty."
            )
        if not isinstance(variable_value, str):
            raise colander.Invalid(
                node,
                "Variable value is not a string."
            )


def _valid_environment_data(node, value):
    if not hasattr(value, 'items'):
        raise colander.Invalid(node, "Environment data is not a mapping.")
    for header, variables in value.items():
        if not isinstance(header, str):
            raise colander.Invalid(node, "Section header is not a string.")
        if not header:
            raise colander.Invalid(node, "Section header is empty.")
        _valid_variables_mapping(node, variables)


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
    context = colander.SchemaNode(colander.String(), missing='')
    post_context = StackTraceFrameContextLinesSchema()
    variables = colander.SchemaNode(
        colander.Mapping(unknown='preserve'),
        validator=_valid_variables_mapping
    )


class StackTraceSchema(colander.SequenceSchema):

    frame = StackTraceFrameSchema()


class ReportSchema(colander.MappingSchema):

    hash = colander.SchemaNode(HexadecimalBinary())
    date = colander.SchemaNode(colander.DateTime())
    message = colander.SchemaNode(colander.String())
    stack_trace = StackTraceSchema()
    environment_data = colander.SchemaNode(
        colander.Mapping(unknown='preserve'),
        validator=_valid_environment_data
    )

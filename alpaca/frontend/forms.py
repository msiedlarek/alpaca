import colander
import deform

from alpaca.frontend.i18n import translate as _


@colander.deferred
def _default_csrf_token(node, kwargs):
    session = kwargs['session']
    return session.get_csrf_token()


@colander.deferred
def _validate_csrf_token(node, kwargs):
    def __validate(value):
        session = kwargs['session']
        if value != session.get_csrf_token():
            return _("CSRF validation error.")
        return True
    return colander.Function(__validate)


class CSRFSecuredSchema(colander.MappingSchema):

    csrf_token = colander.SchemaNode(
        colander.String(),
        default=_default_csrf_token,
        validator=_validate_csrf_token,
        widget=deform.widget.HiddenWidget()
    )

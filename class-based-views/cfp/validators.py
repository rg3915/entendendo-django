from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_not_shouting(value):
    """Recusa título todo em maiúsculas: ninguém precisa gritar."""
    if value.isupper():
        raise ValidationError(
            _("Please don't shout: %(value)s"),
            code="shouting",
            params={"value": value},
        )

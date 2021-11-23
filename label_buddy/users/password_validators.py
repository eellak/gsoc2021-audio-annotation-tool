import re

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _


class NumberValidator(object):

    """
    Custom password validator which ensures that the password will contain
    at least 1 digit.
    """

    def validate(self, password, user=None):
        if not re.findall('\\d', password):
            raise ValidationError(
                _("The password must contain at least 1 digit, 0-9."),
                code='password_no_number',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 digit, 0-9."
        )


class UppercaseValidator(object):

    """
    Custom password validator which ensures that the password will contain
    at least 1 uppercase letter, A-Z.
    """

    def validate(self, password, user=None):
        if not re.findall('[A-Z]', password):
            raise ValidationError(
                _("The password must contain at least 1 uppercase letter, A-Z."),
                code='password_no_upper',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 uppercase letter, A-Z."
        )


class SymbolValidator(object):

    """
    Custom password validator which ensures that the password will contain
    at least 1 symbol.
    """

    def validate(self, password, user=None):
        if not re.findall('[()[\\]{}|\\`~!@#$%^&*_\\-+=;:\'",<>./?]', password):
            raise ValidationError(
                _("The password must contain at least 1 symbol: " + "()[]{}|\\`~!@#$%^&*_-+=;:'\",<>./?"), code='password_no_symbol',)

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 symbol: " + "()[]{}|\\`~!@#$%^&*_-+=;:'\",<>./?")

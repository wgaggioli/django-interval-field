from dateutil.relativedelta import relativedelta
from django import forms
from django.core import validators

from .widgets import IntervalInput
from .util import INTERVAL_UNITS


class IntervalField(forms.Field):
    """Field for time intervals"""
    default_error_messages = {
        'invalid': 'Invalid interval'
    }
    widget = IntervalInput

    def __init__(self, allowed_fields=INTERVAL_UNITS, *args, **kwargs):
        self.max_length = kwargs.pop('max_length', None)
        super(IntervalField, self).__init__(*args, **kwargs)
        self.allowed_fields = allowed_fields

    def _get_allowed(self):
        return self._allowed_fields

    def _set_allowed(self, value):
        self._allowed_fields = list(value)
        self.widget.allowed_fields = [(v, v) for v in self._allowed_fields]

    allowed_fields = property(_get_allowed, _set_allowed)

    def to_python(self, value):
        if value in validators.EMPTY_VALUES:
            return None
        if isinstance(value, relativedelta):
            return value
        # should be a list of value, unit pairs
        if len(value) % 2:
            raise forms.ValidationError(self.error_messages['invalid'])
        params = {}
        for n, u in zip(*[iter(value)] * 2):
            if n in validators.EMPTY_VALUES or u in validators.EMPTY_VALUES:
                continue
            params[u] = int(n)
        if not params:
            return None
        try:
            return relativedelta(**params)
        except (ValueError, TypeError):
            raise forms.ValidationError(self.error_messages['invalid'])

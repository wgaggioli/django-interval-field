import re

from dateutil.relativedelta import relativedelta
from django.db import models
from django.forms import ValidationError

from .util import INTERVAL_UNITS

dt_re = re.compile(r'^(?:\w?\d+ (?:year|mon|week|day|hour|second)s?)+$')


class IntervalField(models.CharField):
    """Used for postgresql's Interval field. Defaults to CharField"""
    description = "Difference between two datetime objects"
    empty_strings_allowed = False
    default_error_messages = {
        'invalid': 'Invalid interval',
    }
    conv_key = {
        'mons': 'months'
    }

    __metaclass__ = models.SubfieldBase

    def __init__(self, allowed_fields=INTERVAL_UNITS,
                 verbose_name=None, name=None, max_length=127, **kwargs):
        self._reverse_conv = None
        self.allowed_fields = allowed_fields
        super(IntervalField, self).__init__(
            verbose_name, name, max_length=max_length, **kwargs)
        self.validators = []

    @property
    def reverse_conv(self):
        if self._reverse_conv is None:
            self._reverse_conv = {}
            for k, v in self.conv_key.items():
                self._reverse_conv[v] = k
        return self._reverse_conv

    def db_type(self, connection):
        if connection.settings_dict['ENGINE'].startswith(
                'django.db.backends.postgres'):
            return 'interval'
        return super(IntervalField, self).db_type(connection)

    def to_python(self, value):
        if value is None:
            return value
        if isinstance(value, relativedelta):
            return value
        if not dt_re.search(value):
            raise ValidationError(self.error_messages['invalid'])
        params = {}
        for n, u in zip(*[iter(value.split(' '))] * 2):
            if not u.endswith('s'):
                u += 's'
            params[self.conv_key.get(u, u)] = int(n)
        try:
            return relativedelta(**params)
        except ValueError:
            raise ValidationError(self.error_messages['invalid'])

    def get_prep_value(self, value):
        if value:
            s = ''
            for field in self.allowed_fields:
                n = getattr(value, field)
                if n:
                    s += '{} {}'.format(n, field)
            return s

    def formfield(self, **kwargs):
        defaults = dict(form_class=IntervalField)
        return super(IntervalField, self).formfield(**defaults)

    def get_internal_type(self):
        return 'CharField'


class HiddenCreditCardField(models.CharField):

    def __init__(self, max_length=31, **kwargs):
        super().__init__(max_length=max_length, **kwargs)

    def to_python(self, value):
        val = super().to_python(value)
        if val and not val.startswith('*'):
            val = (len(val) - 4) * '*' + val[-4:]
        return val

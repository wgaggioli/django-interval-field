from operator import itemgetter

from django.forms import TextInput, Select, MultiWidget

from .util import INTERVAL_UNITS


class IntervalInput(MultiWidget):
    """
    A widget for a time interval
    """
    def __init__(self, attrs=None, allowed_fields=None):
        if allowed_fields is None:
            allowed_fields = [(i, i) for i in INTERVAL_UNITS]
        widgets = [TextInput(attrs=attrs),
                   Select(attrs=attrs, choices=allowed_fields)]
        super(IntervalInput, self).__init__(widgets, attrs)
        self.allowed_fields = allowed_fields
        self.repeat = 1

    def _get_widgets(self):
        return self._widgets * self.repeat

    def _set_widgets(self, widgets):
        self._widgets = list(widgets)

    widgets = property(_get_widgets, _set_widgets)

    def _get_allowed(self):
        return self._allowed_fields

    def _set_allowed(self, value):
        self._allowed_fields = self._widgets[1].choices = list(value)

    allowed_fields = property(_get_allowed, _set_allowed)

    def render(self, name, value, attrs=None):
        if isinstance(value, list) and len(value):
            self.repeat = int(len(value) / 2)
        return super(IntervalInput, self).render(name, value, attrs)

    def _decompress_date(self, value):
        decompressed = []
        for field in self.allowed_fields:
            n = getattr(value, field)
            if n:
                decompressed.extend([n, field])
                self.repeat += 1
        decompressed.extend([None, None])
        return decompressed

    def _decompress_str(self, value):
        allowed = map(itemgetter(0), self.allowed_fields)
        decompressed = []
        for n, u in zip(*[iter(value.split(' '))] * 2):
            if not u.endswith('s'):
                u += 's'
            if u in allowed:
                decompressed.extend([int(n), u])
        return decompressed

    def decompress(self, value):
        if value:
            if isinstance(value, str):
                return self._decompress_str(value)
            else:
                return self._decompress_date(value)
        return [None, None]

    def format_output(self, rendered_widgets):
        return '<br/>'.join(
            w1 + w2 for w1, w2 in zip(*[iter(rendered_widgets)] * 2)
        )

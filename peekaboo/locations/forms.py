import pytz

from django.forms import widgets

from peekaboo.main.models import Location
from peekaboo.main.forms import BaseModelForm


class LocationForm(BaseModelForm):

    class Meta:
        model = Location

    def __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)
        self.fields['timezone'].widget = widgets.Select(
            choices=[(x, x) for x in pytz.all_timezones]
        )
        self.fields['name'].widget.attrs.update({
            'placeholder': 'E.g. Mountain View'
        })
        self.fields['slug'].widget.attrs.update({
            'placeholder': 'E.g. mv'
        })

from django import forms
from .models import Visitor, Location


def _(s):
    # XXX
    return s


class _BaseForm(object):
    def clean(self):
        cleaned_data = super(_BaseForm, self).clean()
        for field in cleaned_data:
            if isinstance(cleaned_data[field], basestring):
                cleaned_data[field] = (
                    cleaned_data[field].replace('\r\n', '\n')
                    .replace(u'\u2018', "'").replace(u'\u2019', "'").strip())

        return cleaned_data


class BaseModelForm(_BaseForm, forms.ModelForm):
    pass


class BaseForm(_BaseForm, forms.Form):
    pass


class SignInForm(BaseModelForm):

    class Meta:
        model = Visitor
        exclude = ('created', 'modified', 'picture')

    def __init__(self, *args, **kwargs):
        super(SignInForm, self).__init__(*args, **kwargs)
        if 'location' in self.fields:
            self.fields['location'].widget = forms.widgets.HiddenInput()
        self.fields['job_title'].widget.attrs['autocomplete'] = 'off'
        self.fields['first_name'].widget.attrs['autocomplete'] = 'off'
        self.fields['first_name'].widget.attrs['spellcheck'] = 'false'
        self.fields['first_name'].widget.attrs['autocorrect'] = 'off'
        self.fields['last_name'].widget.attrs['autocomplete'] = 'off'
        self.fields['last_name'].widget.attrs['spellcheck'] = 'false'
        self.fields['last_name'].widget.attrs['autocorrect'] = 'off'

    def clean(self):
        data = super(SignInForm, self).clean()
        if 'first_name' in data and 'last_name' in data:
            if not (data['first_name'] or data['last_name']):
                raise forms.ValidationError(_(u'A name must be entered'))
        return data


class SignInEditForm(SignInForm):

    class Meta:
        model = Visitor
        exclude = ('created', 'modified', 'picture', 'location')


class PictureForm(BaseModelForm):

    class Meta:
        model = Visitor
        fields = ('picture',)


class CSVUploadForm(BaseForm):

    location = forms.ModelChoiceField(
        queryset=Location.objects
    )
    file = forms.FileField()
    format = forms.ChoiceField(
        choices=(
            ('eventbrite', 'EventBrite'),
        )
    )
    date = forms.DateTimeField(
        required=False,
        help_text=(
            'Optional. Date format is YYYY-MM-DD HH:MM using the '
            '24 hour clock. The time is expected to be local to the '
            'location\'s time zone.'
        )

    )

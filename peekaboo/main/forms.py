from django import forms
from .models import (
    Visitor
)


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
        self.fields['location'].widget = forms.widgets.HiddenInput()

    def clean(self):
        data = super(SignInForm, self).clean()
        if 'first_name' in data and 'last_name' in data:
            if not (data['first_name'] or data['last_name']):
                raise forms.ValidationError(_(u'A name must be entered'))
        return data


class PictureForm(BaseModelForm):

    class Meta:
        model = Visitor
        fields = ('picture',)

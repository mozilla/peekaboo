from jingo import register
from django.template import Context
from django.template.loader import get_template


@register.function
def sheetform(form):
    for field in form.fields:
        label = form.fields[field].label
        form.fields[field].widget.attrs['placeholder'] = label
    template = get_template('sheet/sheetform.html')
    context = Context({'form': form})
    return template.render(context)

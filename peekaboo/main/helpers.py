from jingo import register
from django.template import Context
from django.template.loader import get_template


@register.function
def tabletform(form):
    for field in form.fields:
        label = form.fields[field].label
        form.fields[field].widget.attrs['placeholder'] = label
    template = get_template('main/tabletform.html')
    context = Context({'form': form})
    return template.render(context)


@register.function
def bootstrapform(form):
    template = get_template("bootstrapform/form.html")
    context = Context({'form': form})
    return template.render(context)

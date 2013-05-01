from jingo import register
from django.template import Context
from django.template.loader import get_template
from sorl.thumbnail import get_thumbnail


@register.function
def bootstrapform(form):
    template = get_template("bootstrapform/form.html")
    context = Context({'form': form})
    return template.render(context)


@register.filter
def js_bool(variable):
    return variable and "true" or "false"


@register.function
def thumbnail(filename, geometry, **options):
    try:
        return get_thumbnail(filename, geometry, **options)
    except IOError:
        return None
    except IntegrityError:
        # annoyingly, this happens sometimes because kvstore in sorl
        # doesn't check before writing properly
        # see https://bugzilla.mozilla.org/show_bug.cgi?id=817765
        # try again
        time.sleep(1)
        return thumbnail(filename, geometry, **options)

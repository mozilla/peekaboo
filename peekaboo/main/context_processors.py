from peekaboo.main.models import Location


def main(request):
    return {
        'all_locations': Location.objects.all().order_by('name'),
    }

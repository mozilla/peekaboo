from peekaboo.main.models import Location


def main(request):
    data = {
        'all_locations': Location.objects.all().order_by('name'),
    }
    if request.session.get('default-location'):
        try:
            location = Location.objects.get(
                slug=request.session.get('default-location')
            )
            data['current_location'] = location
        except Location.DoesNotExist:
            pass
    return data

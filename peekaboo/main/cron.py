import cronjobs

from peekaboo.main.recycle import recycle_visits


@cronjobs.register
def recycle():
    recycle_visits()

#
# {{ header }}
#

MAILTO=peterbe@mozilla.com

HOME=/tmp

# Daily
7 0 * * * {{ cron }} recycle 2>&1 | grep -Ev '(DeprecationWarning|UserWarning|from pkg_resources)'


MAILTO=root

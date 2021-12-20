from django.conf import settings
from django.utils.translation import ugettext_lazy as _


def get_setting(name: str, default=None):
    return getattr(settings, "WAGTAIL_ANALYTICS_%s" % name, default)


GA_KEY_CONTENT = get_setting("GA_KEY_CONTENT", default="")

PATH_PREFIX = get_setting("PATH_PREFIX", default="analytics")
MENU_LABEL = get_setting("MENU_LABEL", default=_("Analytics"))
MENU_ORDER = get_setting("MENU_ORDER", default=8000)

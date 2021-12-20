from django.urls import reverse
from wagtail.contrib.settings.forms import SiteSwitchForm as BaseSiteSwitchForm


class SiteSwitchForm(BaseSiteSwitchForm):
    @classmethod
    def get_change_url(cls, site, model):
        return reverse("wagtail-analytics-dashboard", kwargs={"site_id": site.id})

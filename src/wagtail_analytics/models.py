from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy
from wagtail.admin.panels import FieldPanel, HelpPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting

from wagtail_analytics import settings


@register_setting(icon="view")
class AnalyticsSettings(BaseSiteSetting):
    id = models.AutoField(primary_key=True, auto_created=True, verbose_name="ID")

    #: plausible
    plausible_enabled = models.BooleanField(
        verbose_name=_("Plausible Enabled"), default=False
    )
    plausible_domain = models.CharField(
        verbose_name=_("Plausible Domain"), max_length=255, default="plausible.io"
    )

    #: google tag manager
    google_tag_manager_enabled = models.BooleanField(
        verbose_name=_("Google Tag Manager Enabled"), default=False
    )
    google_tag_manager_container_id = models.CharField(
        verbose_name=_("Google Tag Manager Container ID"),
        max_length=255,
        null=True,
        blank=True,
    )

    #: google analaytics
    google_analytics_enabled = models.BooleanField(
        verbose_name=_("Google Analytics Enabled"), default=False
    )
    google_analytics_property_id = models.CharField(
        verbose_name=_("Google Analytics Property ID"),
        max_length=255,
        null=True,
        blank=True,
    )
    google_analytics_measurement_id = models.CharField(
        verbose_name=_("Google Analytics Measurement ID"),
        max_length=255,
        null=True,
        blank=True,
    )

    google_site_verification = models.CharField(
        verbose_name=_("Google Site Verification"),
        max_length=255,
        null=True,
        blank=True,
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("plausible_enabled"),
                FieldPanel("plausible_domain"),
            ],
            heading=_("Plausible"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("google_tag_manager_enabled"),
                FieldPanel("google_tag_manager_container_id"),
            ],
            heading=_("Google Tag Manager"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("google_analytics_enabled"),
                FieldPanel("google_analytics_property_id"),
                FieldPanel("google_analytics_measurement_id"),
            ],
            heading=_("Google Analytics"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("google_site_verification"),
            ],
            heading=_("Google Search Console"),
        ),
    ]

    class Meta:
        verbose_name = _("Analytics")

    @property
    def is_enabled(self):
        if self.plausible_enabled or self.google_analytics_enabled:
            return True
        return False

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy
from wagtail.admin.edit_handlers import FieldPanel, HelpPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSetting, register_setting


@register_setting(icon="view")
class AnalyticsSettings(BaseSetting):
    id = models.AutoField(primary_key=True, auto_created=True, verbose_name="ID")

    google_tag_manager_enabled = models.BooleanField(
        verbose_name=_("Google Tag Manager Enabled"), default=False
    )
    google_tag_manager_container_id = models.CharField(
        verbose_name=_("Google Tag Manager Container ID"),
        max_length=255,
        null=True,
        blank=True,
    )

    google_analytics_enabled = models.BooleanField(
        verbose_name=_("Google Analytics Enabled"), default=False
    )
    google_analytics_property_id = models.CharField(
        verbose_name=_("Google Analytics Property ID"),
        max_length=255,
        null=True,
        blank=True,
    )
    google_analytics_view_id = models.CharField(
        verbose_name=_("Google Analytics View ID"),
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
                FieldPanel("google_tag_manager_enabled"),
                FieldPanel("google_tag_manager_container_id"),
            ],
            heading=_("Google Tag Manager"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("google_analytics_enabled"),
                FieldPanel("google_analytics_property_id"),
                FieldPanel("google_analytics_view_id"),
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

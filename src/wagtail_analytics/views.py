import dataclasses
import json

from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView
from wagtail.admin.panels import HelpPanel, ObjectList, TabbedInterface
from wagtail.models import Page, Site

from wagtail_analytics import settings as wagtail_analytics_settings
from wagtail_analytics.forms import SiteSwitchForm
from wagtail_analytics.lib.analytics import GoogleAnalyticsAPIClient, PlausibleAPIClient
from wagtail_analytics.models import AnalyticsSettings


class SessionsPanel(HelpPanel):
    def __init__(
        self,
        content="",
        template="wagtail_analytics/edit_handlers/sessions.html",
        heading=_("Sessions"),
        classname="",
    ):
        super().__init__(template=template, heading=heading, classname=classname)

    def render(self):
        return mark_safe(
            render_to_string(
                self.template,
                {
                    "id": None,
                    "config_url": reverse("wagtail-analytics-config"),
                },
            )
        )


class AnalyticsPageMixin:
    analytics_panels = [SessionsPanel()]

    edit_handler = TabbedInterface(
        [
            ObjectList(Page.content_panels, heading=_("Content")),
            ObjectList(Page.promote_panels, heading=_("Promote")),
            ObjectList(
                Page.settings_panels,
                heading=_("Settings"),
                classname="settings",
            ),
            ObjectList(analytics_panels, heading=_("Analytics")),
        ]
    )


class DashboardView(TemplateView):
    template_name = "wagtail_analytics/dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        site_id = kwargs.get("site_id", None)

        if not site_id:
            site = Site.objects.get(is_default_site=True)
            return redirect(
                reverse("wagtail-analytics-dashboard", kwargs={"site_id": site.id})
            )

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        site_id = self.kwargs.get("site_id", None)

        if site_id:
            site = get_object_or_404(Site, id=site_id)
        else:
            site = Site.objects.get(is_default_site=True)

        analytics_settings = AnalyticsSettings.for_site(site)

        # Show a site switcher form if there are multiple sites
        site_switcher = None
        if Site.objects.count() > 1:
            site_switcher = SiteSwitchForm(site, Site)

        context.update(
            {
                "is_enabled": analytics_settings.is_enabled,
                "site": site,
                "site_switcher": site_switcher,
                "report_url": reverse(
                    "wagtail-analytics-report", kwargs={"site_id": site.id}
                ),
            }
        )
        return context


class AnalyticsReportView(View):
    def get(self, request, *args, **kwargs):
        site_id = kwargs.get("site_id", None)
        site = get_object_or_404(Site, id=site_id)
        analytics_settings = AnalyticsSettings.for_site(site)

        if analytics_settings.plausible_enabled:
            client = PlausibleAPIClient(
                site.hostname,
                wagtail_analytics_settings.PLAUSIBLE_API_KEY,
            )
            report = client.get_report()
            report_dict = dataclasses.asdict(report)
            return JsonResponse(report_dict)

        if analytics_settings.google_analytics_enabled:
            credentials = json.loads(wagtail_analytics_settings.GA_KEY_CONTENT)
            client = GoogleAnalyticsAPIClient(
                analytics_settings.google_analytics_property_id,
                credentials,
            )
            report = client.get_report()
            report_dict = dataclasses.asdict(report)
            return JsonResponse(report_dict)
        return JsonResponse(status=404)

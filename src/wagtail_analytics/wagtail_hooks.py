from django.contrib.auth.models import Permission
from django.templatetags.static import static
from django.urls import include, path, re_path, reverse
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin.menu import Menu, MenuItem, SubmenuMenuItem

from wagtail_analytics import settings as wagtail_analytics_settings
from wagtail_analytics import views
from wagtail_analytics.models import AnalyticsSettings

wagtail_analytics_menu = Menu(
    register_hook_name="register_wagtail_analytics_menu_item",
    construct_hook_name="construct_wagtail_analytics_menu",
)


class WagtailAnalyticsMenuItem(MenuItem):
    def is_shown(self, request):
        return request.user.has_perm("wagtail_analytics.view_analyticssettings")


@hooks.register("register_permissions")
def register_permissions():
    app = "wagtail_analytics"
    model = "analyticssettings"

    return Permission.objects.filter(
        content_type__app_label=app, codename__in=[f"view_{model}"]
    )


@hooks.register("register_admin_urls")
def urlconf_analytics():
    return [
        path(
            "%s/" % wagtail_analytics_settings.PATH_PREFIX,
            views.DashboardView.as_view(),
            name="wagtail-analytics-dashboard",
        ),
        path(
            "%s/<str:site_id>/" % wagtail_analytics_settings.PATH_PREFIX,
            views.DashboardView.as_view(),
            name="wagtail-analytics-dashboard",
        ),
    ]


@hooks.register("register_admin_menu_item")
def register_menu():
    return SubmenuMenuItem(
        wagtail_analytics_settings.MENU_LABEL,
        wagtail_analytics_menu,
        classnames="icon icon-view",
        order=wagtail_analytics_settings.MENU_ORDER,
    )


@hooks.register("register_wagtail_analytics_menu_item")
def register_menu_item():
    return WagtailAnalyticsMenuItem(
        _("Dashboard"),
        reverse("wagtail-analytics-dashboard"),
        classnames="icon icon-view",
        order=0,
    )


@hooks.register("insert_global_admin_css")
def insert_global_admin_css():
    css_files = ["chart.js/Chart.min.css", "wagtailanalytics/main.css"]
    css_includes = format_html_join(
        "\n",
        '<link rel="stylesheet" href="{0}">',
        ((static(filename),) for filename in css_files),
    )
    return css_includes


@hooks.register("insert_editor_js")
def insert_analytics_js():
    js_files = [
        "chart.js/Chart.bundle.min.js",
        "moment/moment.min.js",
        "wagtailanalytics/main.js",
    ]
    js_includes = format_html_join(
        "\n",
        '<script src="{0}"></script>',
        ((static(filename),) for filename in js_files),
    )
    return js_includes


@hooks.register("register_admin_urls")
def register_api_urls():
    return [
        path(
            "%s/api/<str:site_id>/" % wagtail_analytics_settings.PATH_PREFIX,
            views.AnalyticsReportView.as_view(),
            name="wagtail-analytics-report",
        )
    ]

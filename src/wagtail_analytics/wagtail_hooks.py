from django.templatetags.static import static
from django.urls import include, path, re_path, reverse
from django.utils.html import format_html, format_html_join
from django.utils.translation import ugettext_lazy as _
from wagtail.admin.menu import Menu, MenuItem, SubmenuMenuItem
from wagtail.core import hooks

from wagtail_analytics import settings as wagtail_analytics_settings
from wagtail_analytics import views

wagtail_analytics_menu = Menu(
    register_hook_name="register_wagtail_analytics_menu_item",
    construct_hook_name="construct_wagtail_analytics_menu",
)


class WagtailAnalyticsMenuItem(MenuItem):
    def is_shown(self, request):
        # TODO: Fix permissions
        return request.user.is_superuser


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
        classnames="icon icon-fa-bar-chart",
        order=wagtail_analytics_settings.MENU_ORDER,
    )


@hooks.register("register_wagtail_analytics_menu_item")
def register_menu_item():
    return WagtailAnalyticsMenuItem(
        _("Dashboard"),
        reverse("wagtail-analytics-dashboard"),
        classnames="icon icon-fa-tachometer",
        order=0,
    )


@hooks.register("insert_editor_css")
def insert_analytics_css():
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
def config_url():
    return [
        path(
            "%s/config/<str:page_id>/" % wagtail_analytics_settings.PATH_PREFIX,
            views.ConfigView.as_view(),
            name="wagtail-analytics-config",
        ),
        path(
            "%s/config" % wagtail_analytics_settings.PATH_PREFIX,
            views.ConfigView.as_view(),
            name="wagtail-analytics-config",
        ),
    ]

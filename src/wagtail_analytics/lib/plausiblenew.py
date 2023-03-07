from wagtail_analytics.lib.analytics import (
    PlausibleAnalyticsClient,
    PlausibleRequestData,
    PlausibleRequestDataList,
    WagtailAnalyticsReporter,
)
import os
import ipdb
from datetime import date, timedelta
import dataclasses

# make a request to plausible for a certain site
# site_id = "vicktor.nl" or "vicktor.dev" etc...
api_key = os.environ.get("PLAUSIBLE_API_KEY")
site_url = "vicktor.nl"


def make_request_to_plausible_for_wagtail(site_url, api_key):
    # Dates for plausible
    today = date.today()
    start_this_week = today - timedelta(days=today.weekday())
    end_this_week = start_this_week + timedelta(days=6)
    start_last_week = start_this_week - timedelta(days=7)
    end_last_week = end_this_week - timedelta(days=7)
    this_week_range = f"{start_this_week},{end_this_week}"
    last_week_range = f"{start_last_week},{end_last_week}"

    visitors_this_week = PlausibleRequestData(
        name="visitors_this_week",
        site_id=site_url,
        type="aggregate",
        metrics="visitors",
        period="custom",
        date=this_week_range,
    )

    visitors_last_week = dataclasses.replace(
        visitors_this_week, name="visitors_last_week", date=last_week_range
    )

    most_visited_pages_this_week = PlausibleRequestData(
        name="most_visited_pages_this_week",
        site_id=site_url,
        type="breakdown",
        metrics="visitors",
        period="custom",
        date=this_week_range,
        property="event:page",
        limit=10,
    )
    most_visited_pages_last_week = dataclasses.replace(
        most_visited_pages_this_week,
        name="most_visited_pages_last_week",
        date=last_week_range,
    )
    top_sources_this_week = PlausibleRequestData(
        name="top_sources_this_week",
        site_id=site_url,
        type="breakdown",
        metrics="visitors",
        period="custom",
        date=this_week_range,
        property="visit:source",
        limit=10,
    )
    top_sources_last_week = dataclasses.replace(
        top_sources_this_week, name="top_sources_last_week", date=last_week_range
    )

    # Create a list of requests
    # This is a list of PlausibleRequestData objects
    # This list will give us all the data needed to populate the wagtail analytics dashboard
    wagtail_analytics_request = PlausibleRequestDataList(
        requests=[
            visitors_this_week,
            visitors_last_week,
            most_visited_pages_this_week,
            most_visited_pages_last_week,
            top_sources_this_week,
            top_sources_last_week,
        ]
    )
    client = PlausibleAnalyticsClient(api_key)
    reporter = WagtailAnalyticsReporter(client)
    response = reporter.get_report(wagtail_analytics_request)
    return response


data = make_request_to_plausible_for_wagtail(site_url, api_key)

ipdb.set_trace()

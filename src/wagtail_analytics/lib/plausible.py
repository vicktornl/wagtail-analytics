from wagtail_analytics.lib.analytics import (
    PlausibleAnalyticsClient,
    PlausibleRequestData,
    PlausibleRequestDataList,
)
import os
import ipdb
from datetime import date, timedelta

# make a request to plausible for a certain site
# site_id = "vicktor.nl" or "vicktor.dev" etc...


def make_request_to_plausible_for_wagtail(site_url):
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
    visitors_last_week = PlausibleRequestData(
        name="visitors_last_week",
        site_id=site_url,
        type="aggregate",
        metrics="visitors",
        period="custom",
        date=last_week_range,
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
    most_visited_pages_last_week = PlausibleRequestData(
        name="most_visited_pages_last_week",
        site_id=site_url,
        type="breakdown",
        metrics="visitors",
        period="custom",
        date=last_week_range,
        property="event:page",
        limit=10,
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
    top_sources_last_week = PlausibleRequestData(
        name="top_sources_last_week",
        site_id=site_url,
        type="breakdown",
        metrics="visitors",
        period="custom",
        date=last_week_range,
        property="visit:source",
        limit=10,
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

    # Make the request using the list of PlausibleRequestData objects
    api_key = os.environ.get("PLAUSIBLE_API_KEY")
    request = PlausibleAnalyticsClient(api_key).get_wagtail_report(
        wagtail_analytics_request
    )

    return request


data = make_request_to_plausible_for_wagtail("vicktor.nl")

ipdb.set_trace()

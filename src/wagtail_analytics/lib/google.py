from wagtail_analytics.lib.analytics import (
    GoogleAnalyticsClient,
    GoogleRequestData,
    GoogleRequestDataList,
    WagtailAnalyticsReporter,
)
import os
import ipdb
from datetime import date, timedelta
import dataclasses

property_id = "279726693"
# for this to work u need a credentials json for the api and set the env variable to the path of the json
# export GOOGLE_APPLICATION_CREDENTIALS="[PATH]"
def make_request_to_google_for_wagtail(property_id):

    visitors_this_week = GoogleRequestData(
        name="visitors_this_week",
        property_id=property_id,
        dimensions=["country"],
        metrics=["activeUsers"],
        start_date="7daysAgo",
        end_date="today",
    )
    visitors_last_week = dataclasses.replace(
        visitors_this_week,
        name="visitors_last_week",
        start_date="14daysAgo",
        end_date="7daysAgo",
    )
    most_visited_pages_this_week = GoogleRequestData(
        name="most_visited_pages_this_week",
        property_id=property_id,
        dimensions=["pagePath"],
        metrics=["activeUsers"],
        start_date="7daysAgo",
        end_date="today",
    )
    most_visited_pages_last_week = dataclasses.replace(
        most_visited_pages_this_week,
        name="most_visited_pages_last_week",
        start_date="14daysAgo",
        end_date="7daysAgo",
    )
    top_sources_this_week = GoogleRequestData(
        name="top_sources_this_week",
        property_id=property_id,
        dimensions=["firstUserSource"],
        metrics=["activeUsers"],
        start_date="7daysAgo",
        end_date="today",
    )
    top_sources_last_week = dataclasses.replace(
        top_sources_this_week,
        name="top_sources_last_week",
        start_date="14daysAgo",
        end_date="7daysAgo",
    )

    wagtail_analytics_request = GoogleRequestDataList(
        requests=[
            visitors_this_week,
            visitors_last_week,
            most_visited_pages_this_week,
            most_visited_pages_last_week,
            top_sources_this_week,
            top_sources_last_week,
        ]
    )

    client = GoogleAnalyticsClient()
    reporter = WagtailAnalyticsReporter(client)
    response = reporter.get_report(wagtail_analytics_request)
    return response


data = make_request_to_google_for_wagtail(property_id)

ipdb.set_trace()

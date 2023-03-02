from wagtail_analytics.lib.analytics import PlausibleAnalyticsClient, PlausibleRequestData, PlausibleRequestDataList
import os
import ipdb
from datetime import date, timedelta
# Dates for plausible

today = date.today()
start_this_week = today - timedelta(days=today.weekday())
end_this_week = start_this_week + timedelta(days=6)
start_last_week = start_this_week - timedelta(days=7)
end_last_week = end_this_week - timedelta(days=7)

# Number of visitors from this week and last week:

visitors_this_week = PlausibleRequestData(
    site_id="vicktor.nl",
    type="aggregate",
    metrics="visitors",
    period="custom",
    date=f"{start_this_week},{end_this_week}", 
)

visitors_last_week = PlausibleRequestData(
    site_id="vicktor.nl",
    type="aggregate",
    metrics="visitors",
    period="custom",
    date=f"{start_last_week},{end_last_week}",
)

# Most visited pages this week and last week:

most_visited_pages_this_week = PlausibleRequestData(
    site_id="vicktor.nl",
    type="breakdown",
    metrics="visitors",
    period="custom",
    date=f"{start_this_week},{end_this_week}",
    property="event:page",
    limit=10,
)

most_visited_pages_last_week = PlausibleRequestData(
    site_id="vicktor.nl",
    type="breakdown",
    metrics="visitors",
    period="custom",
    date=f"{start_last_week},{end_last_week}",
    property="event:page",
    limit=10,
)

# Top 10 sources this week and last week:

top_sources_this_week = PlausibleRequestData(
    site_id="vicktor.nl",
    type="breakdown",
    metrics="visitors",
    period="custom",
    date=f"{start_this_week},{end_this_week}",
    property="visit:source",
    limit=10,
)

top_sources_last_week = PlausibleRequestData(
    site_id="vicktor.nl",
    type="breakdown",
    metrics="visitors",
    period="custom",
    date=f"{start_last_week},{end_last_week}",
    property="visit:source",
    limit=10,
)


# Create a list of requests
request_list = PlausibleRequestDataList(
    requests=[
        visitors_this_week,
        visitors_last_week,
        most_visited_pages_this_week,
        most_visited_pages_last_week,
        top_sources_this_week,
        top_sources_last_week,
    ]
)

# Example request for plausible
api_key = os.environ.get("PLAUSIBLE_API_KEY")
request = PlausibleAnalyticsClient(
    api_key
).get_report(visitors_this_week)

ipdb.set_trace()
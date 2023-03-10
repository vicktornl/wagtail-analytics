import ipdb

from wagtail_analytics.lib.analytics import GoogleAnalyticsAPIClient

property_id = "279726693"
# for this to work u need a credentials json for the api and set the env variable to the path of the json
# export GOOGLE_APPLICATION_CREDENTIALS="[PATH]"

client = GoogleAnalyticsAPIClient(property_id)
data = client.get_report()

ipdb.set_trace()

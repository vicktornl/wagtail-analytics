from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

import ipdb
import requests
from django.core.exceptions import ImproperlyConfigured
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)

today = date.today()
start_this_week = today - timedelta(days=today.weekday())
end_this_week = start_this_week + timedelta(days=6)
start_last_week = start_this_week - timedelta(days=7)
end_last_week = end_this_week - timedelta(days=7)
this_week_range = f"{start_this_week},{end_this_week}"
last_week_range = f"{start_last_week},{end_last_week}"


@dataclass
class TopPage:
    url: str
    pageviews: int


@dataclass
class TopSource:
    name: str
    pageviews: int


@dataclass
class Report:
    visitors_this_week: List[Tuple[datetime, int]]
    visitors_last_week: List[Tuple[datetime, int]]
    top_pages: List[TopPage]
    top_sources: List[TopSource]


class APIClient(ABC):
    def get_report(self) -> Report:
        visitors_this_week = self.get_visitors_this_week()
        visitors_last_week = self.get_visitors_last_week()
        top_pages = self.get_top_pages()
        top_sources = self.get_top_sources()
        report = Report(
            visitors_this_week=visitors_this_week,
            visitors_last_week=visitors_last_week,
            top_pages=top_pages,
            top_sources=top_sources,
        )
        return report

    @abstractmethod
    def get_visitors_this_week(self) -> List[Tuple[datetime, int]]:
        return []

    @abstractmethod
    def get_visitors_last_week(self) -> List[Tuple[datetime, int]]:
        return []

    @abstractmethod
    def get_top_pages(self) -> List[TopPage]:
        return []

    @abstractmethod
    def get_top_sources(self) -> List[TopSource]:
        return []


class PlausibleAPIClient(APIClient):
    base_url = "https://plausible.io/api/v1/stats"

    def __init__(self, site_id, api_key) -> None:
        self.site_id = site_id
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def get_visitors_this_week(self) -> List[Tuple[datetime, int]]:
        visitors_this_week = []

        url_this_week = "{base_url}/timeseries?date={range}&site_id={site_id}&period=custom&metrics=visitors".format(
            range=this_week_range, base_url=self.base_url, site_id=self.site_id
        )
        visitor_this_week_response = requests.get(
            url_this_week, headers=self.headers
        ).json()
        for day in visitor_this_week_response["results"]:
            visitors_this_week.append((day["date"], day["visitors"]))

        return visitors_this_week

    def get_visitors_last_week(self) -> List[Tuple[datetime, int]]:
        visitors_last_week = []

        url_last_week = "{base_url}/timeseries?date={range}&site_id={site_id}&period=custom&metrics=visitors".format(
            range=last_week_range, base_url=self.base_url, site_id=self.site_id
        )
        visitor_last_week_response = requests.get(
            url_last_week, headers=self.headers
        ).json()
        for day in visitor_last_week_response["results"]:
            visitors_last_week.append((day["date"], day["visitors"]))

        return visitors_last_week

    def get_top_pages(self) -> List[TopPage]:

        top_pages = []

        url_top_pages = "{base_url}/breakdown?limit=10&date={range}&site_id={site_id}&period=custom&metrics=visitors&property=event:page".format(
            range=this_week_range, base_url=self.base_url, site_id=self.site_id
        )
        response = requests.get(url_top_pages, headers=self.headers).json()
        for page in response["results"]:
            top_pages.append(TopPage(url=page["page"], pageviews=page["visitors"]))
        return top_pages

    def get_top_sources(self) -> List[TopSource]:

        top_sources = []

        url_top_sources = "{base_url}/breakdown?limit=10&date={range}&site_id={site_id}&period=custom&metrics=visitors&property=visit:source".format(
            range=this_week_range, base_url=self.base_url, site_id=self.site_id
        )
        response = requests.get(url_top_sources, headers=self.headers).json()
        for source in response["results"]:
            top_sources.append(
                TopSource(name=source["source"], pageviews=source["visitors"])
            )
        return top_sources

    def get_report(self) -> Report:
        return super().get_report()


# for this to work u need a credentials json for the api and set the env variable to the path of the json
# export GOOGLE_APPLICATION_CREDENTIALS="[PATH]"
class GoogleAnalyticsAPIClient(APIClient):
    client = BetaAnalyticsDataClient()

    def __init__(self, propery_id) -> None:
        self.property_id = propery_id

    def get_visitors_this_week(self) -> List[Tuple[datetime, int]]:
        visitors_this_week = []

        visitors_this_week_request = RunReportRequest(
            property="properties/" + self.property_id,
            date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
            dimensions=[Dimension(name="date")],
            metrics=[Metric(name="activeUsers")],
        )
        visitors_this_week_response = self.client.run_report(visitors_this_week_request)
        for row in visitors_this_week_response.rows:
            visitors_this_week.append((row.dimension_values[0], row.metric_values[0]))
        return visitors_this_week

    def get_visitors_last_week(self) -> List[Tuple[datetime, int]]:
        visitors_last_week = []

        visitors_last_week_request = RunReportRequest(
            property="properties/" + self.property_id,
            date_ranges=[DateRange(start_date="14daysAgo", end_date="7daysAgo")],
            dimensions=[Dimension(name="date")],
            metrics=[Metric(name="activeUsers")],
        )
        visitors_last_week_response = self.client.run_report(visitors_last_week_request)
        for row in visitors_last_week_response.rows:
            visitors_last_week.append((row.dimension_values[0], row.metric_values[0]))
        return visitors_last_week

    def get_top_pages(self) -> List[TopPage]:
        top_pages = []

        top_pages_request = RunReportRequest(
            property="properties/" + self.property_id,
            date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
            dimensions=[Dimension(name="pagePath")],
            metrics=[Metric(name="activeUsers")],
            limit=10,
        )
        response = self.client.run_report(top_pages_request)
        for row in response.rows:
            top_pages.append(
                TopPage(
                    url=row.dimension_values[0].value,
                    pageviews=row.metric_values[0].value,
                )
            )
        return top_pages

    def get_top_sources(self) -> List[TopSource]:
        top_sources = []

        top_sources_request = RunReportRequest(
            property="properties/" + self.property_id,
            date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
            dimensions=[Dimension(name="pagePath")],
            metrics=[Metric(name="activeUsers")],
            limit=10,
        )
        response = self.client.run_report(top_sources_request)
        for row in response.rows:
            top_sources.append(
                TopSource(
                    name=row.dimension_values[0].value,
                    pageviews=row.metric_values[0].value,
                )
            )
        return top_sources

    def get_report(self) -> Report:
        return super().get_report()

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Literal
from django.core.exceptions import ImproperlyConfigured
import requests
import ipdb
from datetime import date, timedelta
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from abc import ABC, abstractmethod


@dataclass
class PlausibleRequestData:
    name: str
    site_id: str
    type: Literal["aggregate", "breakdown", "realtime", "timeseries"] = field(
        default="aggregate"
    )
    metrics: Literal[
        "visitors", "pageviews", "bounce_rate", "visits", "events"
    ] = field(default="visitors")
    period: str = field(default="30d")
    date: str = field(default="today")
    property: Optional[str] = field(default=None)
    filters: Optional[str] = field(default=None)
    limit: Optional[int] = field(default=None)


@dataclass
class PlausibleRequestDataList:
    requests: List[PlausibleRequestData]


@dataclass
class PlausibleRequest:
    url: str
    params: Dict[str, Any]
    headers: Dict[str, Any]


@dataclass
class GoogleRequestData:
    name: str
    property_id: str
    dimensions: List[str]
    metrics: List[str]
    start_date: str
    end_date: str


@dataclass
class GoogleRequestDataList:
    requests: List[GoogleRequestData]


@dataclass
class Report:
    name: str
    data: List[Dict[str, Any]]


@dataclass
class Wagtail_Analytics_Report:
    visitors_this_week: int
    visitors_last_week: int
    most_visited_pages_last_week: List[Dict[str, Any]]
    most_visited_pages_this_week: List[Dict[str, Any]]
    top_sources_this_week: List[Dict[str, Any]]
    top_sources_last_week: List[Dict[str, Any]]


class BaseAnalyticsClient(ABC):
    @abstractmethod
    def create_request(
        self, request_data: Union[PlausibleRequestData, GoogleRequestData, Any]
    ):
        pass

    @abstractmethod
    def send_request(self, request: Union[PlausibleRequest, GoogleRequestData, Any]):
        pass

    @abstractmethod
    def get_report(
        self, request_data: Union[PlausibleRequestData, GoogleRequestData, Any]
    ):
        pass


class PlausibleAnalyticsClient(BaseAnalyticsClient):
    base_url = "https://plausible.io/api/v1/stats/"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def create_request(self, request_data: PlausibleRequestData):
        endpoint = self.base_url + request_data.type + "?"
        params = {
            "site_id": request_data.site_id,
            "filters": request_data.filters,
            "period": request_data.period,
            "metrics": request_data.metrics,
            "property": request_data.property,
            "date": request_data.date,
            "limit": request_data.limit,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        request = PlausibleRequest(endpoint, params, headers)
        return request

    def send_request(self, request: PlausibleRequest):
        url = f"{request.url}"
        response = requests.get(url, params=request.params, headers=request.headers)
        if response.status_code != 200:
            raise ImproperlyConfigured(
                f"Error while requesting {request} error: {response.status_code}"
            )
        return response.json()

    def get_report(self, requests: PlausibleRequestData):
        report = Report(requests.name, self.send_request(self.create_request(requests)))
        return report


# for this to work u need a credentials json for the api and set the env variable to the path of the json
# export GOOGLE_APPLICATION_CREDENTIALS="[PATH]"
class GoogleAnalyticsClient(BaseAnalyticsClient):
    def create_request(self, request_data: GoogleRequestData):
        request = RunReportRequest(
            property=f"properties/{request_data.property_id}",
            dimensions=[
                Dimension(name=dimension) for dimension in request_data.dimensions
            ],
            metrics=[Metric(name=metric) for metric in request_data.metrics],
            date_ranges=[
                DateRange(
                    start_date=request_data.start_date, end_date=request_data.end_date
                )
            ],
        )
        return request

    def send_request(self, request: RunReportRequest):
        try:
            client = BetaAnalyticsDataClient()
            response = client.run_report(request)
            return response
        except Exception as e:
            raise ImproperlyConfigured(
                f"Error while requesting {request} error: {e}"
            ) from e

    def get_report(self, request_data: GoogleRequestData):
        report = Report(
            request_data.name, self.send_request(self.create_request(request_data))
        )
        return report


# this is a class that can be used to get reports from both plausible and google analytics
# it can be used like this
# client = PlausibleAnalyticsClient(api_key)
# reporter = WagtailAnalyticsReporter(client)
# request_data_list = PlausibleRequestDataList(requests=[request_data1, request_data2])
# reporter.get_report(request_data_list)
class WagtailAnalyticsReporter:
    reports: List[Report]
    wagtail_report: Wagtail_Analytics_Report

    def __init__(self, client: Union[PlausibleAnalyticsClient, GoogleAnalyticsClient]):
        self.client = client
        self.reports = []

    def get_report(
        self, request_data_list: Union[PlausibleRequestDataList, GoogleRequestDataList]
    ):
        if isinstance(self.client, PlausibleAnalyticsClient):
            for request_data in request_data_list.requests:
                self.reports.append(self.client.get_report(request_data))
                self.wagtail_report = PlausibleAnalyticsReportMapper().map_reports(
                    self.reports
                )
            return self.wagtail_report

        elif isinstance(self.client, GoogleAnalyticsClient):
            for request_data in request_data_list.requests:
                self.reports.append(self.client.get_report(request_data))
            return self.mapper_google_analytics(self.reports)

    def mapper_google_analytics(self, reports: List[Report]):
        wagtail_report = Wagtail_Analytics_Report(0, 0, [], [], [], [])
        for report in reports:
            if report.name == "visitors_this_week":
                for row in report.data.rows:
                    wagtail_report.visitors_this_week += int(row.metric_values[0].value)
            elif report.name == "visitors_last_week":
                for row in report.data.rows:
                    wagtail_report.visitors_last_week += int(row.metric_values[0].value)
            elif report.name == "most_visited_pages_this_week":
                for row in report.data.rows:
                    wagtail_report.most_visited_pages_this_week.append(
                        {
                            "page": row.dimension_values[0].value,
                            "visitors": row.metric_values[0].value,
                        }
                    )
            elif report.name == "most_visited_pages_last_week":
                for row in report.data.rows:
                    wagtail_report.most_visited_pages_last_week.append(
                        {
                            "page": row.dimension_values[0].value,
                            "visitors": row.metric_values[0].value,
                        }
                    )
            elif report.name == "top_sources_this_week":
                for row in report.data.rows:
                    wagtail_report.top_sources_this_week.append(
                        {
                            "source": row.dimension_values[0].value,
                            "visitors": row.metric_values[0].value,
                        }
                    )
            elif report.name == "top_sources_last_week":
                for row in report.data.rows:
                    wagtail_report.top_sources_last_week.append(
                        {
                            "source": row.dimension_values[0].value,
                            "visitors": row.metric_values[0].value,
                        }
                    )
        return wagtail_report


@abstractmethod
class PlausibleMapper(ABC):
    def map_report(self, report: Report, wagtail_report: Wagtail_Analytics_Report):
        pass


class VisitorsThisWeekMapper(PlausibleMapper):
    def map_report(self, report: Report, wagtail_report: Wagtail_Analytics_Report):
        wagtail_report.visitors_this_week = report.data["results"]["visitors"]["value"]


class VisitorsLastWeekMapper(PlausibleMapper):
    def map_report(self, report: Report, wagtail_report: Wagtail_Analytics_Report):
        wagtail_report.visitors_last_week = report.data["results"]["visitors"]["value"]


class MostVisitedPagesThisWeekMapper(PlausibleMapper):
    def map_report(self, report: Report, wagtail_report: Wagtail_Analytics_Report):
        wagtail_report.most_visited_pages_this_week = report.data["results"]


class MostVisitedPagesLastWeekMapper(PlausibleMapper):
    def map_report(self, report: Report, wagtail_report: Wagtail_Analytics_Report):
        wagtail_report.most_visited_pages_last_week = report.data["results"]


class TopSourcesThisWeekMapper(PlausibleMapper):
    def map_report(self, report: Report, wagtail_report: Wagtail_Analytics_Report):
        wagtail_report.top_sources_this_week = report.data["results"]


class TopSourcesLastWeekMapper(PlausibleMapper):
    def map_report(self, report: Report, wagtail_report: Wagtail_Analytics_Report):
        wagtail_report.top_sources_last_week = report.data["results"]


class PlausibleMapperFactory:
    def __init__(self):
        self.mappers = {
            "visitors_this_week": VisitorsThisWeekMapper(),
            "visitors_last_week": VisitorsLastWeekMapper(),
            "most_visited_pages_this_week": MostVisitedPagesThisWeekMapper(),
            "most_visited_pages_last_week": MostVisitedPagesLastWeekMapper(),
            "top_sources_this_week": TopSourcesThisWeekMapper(),
            "top_sources_last_week": TopSourcesLastWeekMapper(),
        }

    def get_mapper(self, report_name: str):
        return self.mappers.get(report_name, None)


class PlausibleAnalyticsReportMapper:
    def __init__(self):
        self.wagtail_report = Wagtail_Analytics_Report(0, 0, [], [], [], [])

    def map_reports(self, reports: List[Report]):
        for report in reports:
            mapper = PlausibleMapperFactory().get_mapper(report.name)
            mapper.map_report(report, self.wagtail_report)
        return self.wagtail_report

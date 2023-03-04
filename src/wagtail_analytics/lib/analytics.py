from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Literal
from django.core.exceptions import ImproperlyConfigured
import requests
import os
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
    property: Optional[str] = None
    filters: Optional[str] = None
    limit: Optional[int] = None


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
class ReportData:
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
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def do_request():
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def get_report(
        self, request_data: Union[PlausibleRequestData, GoogleRequestData, Any]
    ):
        return ReportData(
            request_data.name, self.do_request(self.create_request(request_data))
        )

    @abstractmethod
    def get_wagtail_report(
        self, request_data: Union[PlausibleRequestDataList, GoogleRequestDataList, Any]
    ):
        return Wagtail_Analytics_Report(0, 0, [], [], [], [])


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

    def do_request(self, request: PlausibleRequest):
        url = f"{request.url}"
        response = requests.get(url, params=request.params, headers=request.headers)
        if response.status_code != 200:
            error_data = {
                "error_code": response.status_code,
                "error_message": response.text,
            }
            raise ImproperlyConfigured(error_data)
        return response.json()

    def get_report(self, requests: PlausibleRequestData):
        report = ReportData(
            requests.name, self.do_request(self.create_request(requests))
        )
        return report

    def get_wagtail_report(self, requests: PlausibleRequestDataList):
        report = Wagtail_Analytics_Report(0, 0, [], [], [], [])
        for request in requests.requests:
            if request.name == "visitors_this_week":
                response_data = self.do_request(self.create_request(request))
                report.visitors_this_week = response_data["results"]["visitors"][
                    "value"
                ]
            elif request.name == "visitors_last_week":
                response_data = self.do_request(self.create_request(request))
                report.visitors_last_week = response_data["results"]["visitors"][
                    "value"
                ]
            elif request.name == "most_visited_pages_this_week":
                response_data = self.do_request(self.create_request(request))
                report.most_visited_pages_this_week = response_data["results"]
            elif request.name == "most_visited_pages_last_week":
                response_data = self.do_request(self.create_request(request))
                report.most_visited_pages_last_week = response_data["results"]
            elif request.name == "top_sources_this_week":
                response_data = self.do_request(self.create_request(request))
                report.top_sources_this_week = response_data["results"]
            elif request.name == "top_sources_last_week":
                response_data = self.do_request(self.create_request(request))
                report.top_sources_last_week = response_data["results"]
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

    def do_request(self, request):
        client = BetaAnalyticsDataClient()
        response = client.run_report(request)
        return response

    def get_report(self, request_data: GoogleRequestData):
        report = ReportData(
            request_data.name, self.do_request(self.create_request(request_data))
        )
        return report

    def get_wagtail_report(self, request_data: GoogleRequestDataList):
        report = Wagtail_Analytics_Report(0, 0, [], [], [], [])
        for request in request_data.requests:
            if request.name == "visitors_this_week":
                response_data = self.do_request(self.create_request(request))
                for row in response_data.rows:
                    report.visitors_this_week = row.metric_values[0].value
            elif request.name == "visitors_last_week":
                response_data = self.do_request(self.create_request(request))
                for row in response_data.rows:
                    report.visitors_last_week = row.metric_values[0].value
            elif request.name == "most_visited_pages_this_week":
                response_data = self.do_request(self.create_request(request))
                for row in response_data.rows:
                    report.most_visited_pages_this_week.append(
                        {
                            "page": row.dimension_values[0].value,
                            "visitors": row.metric_values[0].value,
                        }
                    )
            elif request.name == "most_visited_pages_last_week":
                response_data = self.do_request(self.create_request(request))
                for row in response_data.rows:
                    report.most_visited_pages_last_week.append(
                        {
                            "page": row.dimension_values[0].value,
                            "visitors": row.metric_values[0].value,
                        }
                    )
            elif request.name == "top_sources_this_week":
                response_data = self.do_request(self.create_request(request))
                for row in response_data.rows:
                    report.top_sources_this_week.append(
                        {
                            "source": row.dimension_values[0].value,
                            "visitors": row.metric_values[0].value,
                        }
                    )
            elif request.name == "top_sources_last_week":
                response_data = self.do_request(self.create_request(request))
                for row in response_data.rows:
                    report.top_sources_last_week.append(
                        {
                            "source": row.dimension_values[0].value,
                            "visitors": row.metric_values[0].value,
                        }
                    )
        return report

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Literal
from django.core.exceptions import ImproperlyConfigured
import requests
import os
import ipdb
from datetime import date, timedelta
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build


@dataclass
class PlausibleRequestData:
    site_id: str
    base_url: str = "https://plausible.io/api/v1/stats/"
    type: Literal["aggregate", "breakdown", "realtime", "timeseries"] = field(default="aggregate")
    metrics: Literal["visitors", "pageviews", "bounce_rate", "visits", "events"] = field(default="visitors")
    period: str = field(default="30d")
    date: str = field(default="today")
    property: Optional[str] = None
    filters: Optional[str] = None
    limit: Optional[int] = None

@dataclass
class GoogleRequestData:
    view_id: str
    base_url: str = "https://analyticsreporting.googleapis.com/v4/reports:batchGet"
    metrics: str = field(default="ga:sessions")
    start_date: str = field(default="7daysAgo")
    end_date: str = field(default="today") 
    dimensions: str = field(default="ga:pagePath")
    filters: Optional[str] = None 

@dataclass
class PlausibleRequestDataList:
    requests: List[PlausibleRequestData]

@dataclass
class GoogleRequestDataList:
    requests: List[GoogleRequestData]

@dataclass
class Report:
    visitors_this_week: int
    visitors_last_week: int
    most_visited_pages_last_week: List[Dict[str, Any]]
    most_visited_pages_this_week: List[Dict[str, Any]]
    top_sources_this_week: List[Dict[str, Any]]
    top_sources_last_week: List[Dict[str, Any]]

class BaseApiClient:

    def create_request(self, request_data: Union[PlausibleRequestData, GoogleRequestData, Any]):
        raise NotImplementedError("Subclasses must implement this method")

    def make_request(self, endpoint: str, params: Dict[str, Any], headers: Dict[str, Any]):
        raise NotImplementedError("Subclasses must implement this method")
    
    def build_report(self, response_data: dict, request_data: Union[PlausibleRequestData, GoogleRequestData, Any]):
        raise NotImplementedError("Subclasses must implement this method")
    
    def get_report(self, request_data: Union[PlausibleRequestData, GoogleRequestData, Any]):
        raise NotImplementedError("Subclasses must implement this method")


class PlausibleAnalyticsClient(BaseApiClient):

    def __init__(self, api_key: str):
        self.api_key = api_key

    def create_request(self, request_data: PlausibleRequestData):
        base_url = request_data.base_url + request_data.type + "?"
        endpoint = base_url
        params = {
            "site_id": request_data.site_id,
            "filters": request_data.filters,
            "period": request_data.period,
            "metrics": request_data.metrics,
            "property": request_data.property,
            "filters": request_data.filters,
            "date": request_data.date,
            "limit": request_data.limit,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response_data = self.make_request(endpoint, params, headers)
        return response_data
    
    def make_request(self, endpoint: str, params: dict, headers: dict):
        url = f"{endpoint}"
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            error_data = {"error_code": response.status_code, "error_message": response.text}
            raise ImproperlyConfigured(error_data)
        return response.json()
    
    def build_report(self, requests: PlausibleRequestDataList):
        for request in requests:
            response_data = self.create_request(request)
    
    def get_report(self, request_data: PlausibleRequestData):
        response_data = self.create_request(request_data)
        return response_data

    

class GoogleAnalyticsClient(BaseApiClient):

    def create_request(self, request_data: GoogleRequestData):
        # Create credentials for the service account.
        credentials = service_account.Credentials.from_service_account_file(
            'key.json', scopes=['https://www.googleapis.com/auth/analytics.readonly'])

        # Create the Analytics API client object.
        analytics = build('analyticsreporting', 'v4', credentials=credentials)

        response = analytics.reports().batchGet(
        body={
            'reportRequests': [
                {
                    'viewId': request_data.view_id,
                    'dateRanges': [{'startDate': request_data.start_date, 'endDate': request_data.end_date}],
                    'metrics': [{'expression': request_data.metrics}],
                    'dimensions': [{'name': request_data.dimensions}],
                    'orderBys': [{'fieldName': request_data.metrics, 'sortOrder': 'DESCENDING'}],
                    'pageSize': 10
                }]
        }
        ).execute()
        report = Report(results=response["reports"][0]["data"]["rows"])
        return report

    def make_request(self, endpoint: str, params: dict, headers: dict):
        pass

    def build_report(self, response_data: dict, request_data: GoogleRequestData):
        pass

    def get_report(self, request_data: GoogleRequestData):
        report = self.create_request(request_data)
        return report
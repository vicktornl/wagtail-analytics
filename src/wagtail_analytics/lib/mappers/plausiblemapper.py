from abc import ABC, abstractmethod


# this is a class that can be used to map reports from plausible to a wagtail analytics report object


class PlausibleMapper(ABC):
    @abstractmethod
    def map_report(self, report, wagtail_report):
        pass


class VisitorsThisWeekMapper(PlausibleMapper):
    def map_report(self, report, wagtail_report):
        wagtail_report.visitors_this_week = report.data["results"]["visitors"]["value"]


class VisitorsLastWeekMapper(PlausibleMapper):
    def map_report(self, report, wagtail_report):
        wagtail_report.visitors_last_week = report.data["results"]["visitors"]["value"]


class MostVisitedPagesThisWeekMapper(PlausibleMapper):
    def map_report(self, report, wagtail_report):
        wagtail_report.most_visited_pages_this_week = report.data["results"]


class MostVisitedPagesLastWeekMapper(PlausibleMapper):
    def map_report(self, report, wagtail_report):
        wagtail_report.most_visited_pages_last_week = report.data["results"]


class TopSourcesThisWeekMapper(PlausibleMapper):
    def map_report(self, report, wagtail_report):
        wagtail_report.top_sources_this_week = report.data["results"]


class TopSourcesLastWeekMapper(PlausibleMapper):
    def map_report(self, report, wagtail_report):
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


# This is the class that is used to map the reports from plausible to wagtail analytics reports
# It takes a list of report objects and a wagtail analytics report object
# It then maps the reports to the wagtail analytics report object
class PlausibleAnalyticsReportMapper:
    def __init__(self, reports, wagtail_report):
        self.reports = reports
        self.wagtail_report = wagtail_report

    def map_reports(self):
        for report in self.reports:
            mapper = PlausibleMapperFactory().get_mapper(report.name)
            mapper.map_report(report, self.wagtail_report)
        return self.wagtail_report

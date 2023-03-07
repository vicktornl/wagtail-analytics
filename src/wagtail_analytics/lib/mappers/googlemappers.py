from abc import ABC, abstractmethod


# this is a class that can be used to map reports from google analytics to wagtail analytics reports


class GoogleAnalyticsMapper(ABC):
    @abstractmethod
    def map_report(self, report, wagtail_report):
        pass


class VisitorsThisWeekMapper(GoogleAnalyticsMapper):
    def map_report(self, report, wagtail_report):
        for row in report.data.rows:
            wagtail_report.visitors_this_week += int(row.metric_values[0].value)


class VisitorsLastWeekMapper(GoogleAnalyticsMapper):
    def map_report(self, report, wagtail_report):
        for row in report.data.rows:
            wagtail_report.visitors_last_week += int(row.metric_values[0].value)


class MostVisitedPagesThisWeekMapper(GoogleAnalyticsMapper):
    def map_report(self, report, wagtail_report):
        for row in report.data.rows:
            wagtail_report.most_visited_pages_this_week.append(
                {
                    "page": row.dimension_values[0].value,
                    "visitors": row.metric_values[0].value,
                }
            )


class MostVisitedPagesLastWeekMapper(GoogleAnalyticsMapper):
    def map_report(self, report, wagtail_report):
        for row in report.data.rows:
            wagtail_report.most_visited_pages_last_week.append(
                {
                    "page": row.dimension_values[0].value,
                    "visitors": row.metric_values[0].value,
                }
            )


class TopSourcesThisWeekMapper(GoogleAnalyticsMapper):
    def map_report(self, report, wagtail_report):
        for row in report.data.rows:
            wagtail_report.top_sources_this_week.append(
                {
                    "source": row.dimension_values[0].value,
                    "visitors": row.metric_values[0].value,
                }
            )


class TopSourcesLastWeekMapper(GoogleAnalyticsMapper):
    def map_report(self, report, wagtail_report):
        for row in report.data.rows:
            wagtail_report.top_sources_last_week.append(
                {
                    "source": row.dimension_values[0].value,
                    "visitors": row.metric_values[0].value,
                }
            )


class GoogleAnalyticsMapperFactory:
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


class GoogleAnalyticsReportMapper:
    def __init__(self, reports, wagtail_report):
        self.reports = reports
        self.wagtail_report = wagtail_report

    def map_reports(self, reports):
        for report in reports:
            mapper = GoogleAnalyticsMapperFactory().get_mapper(report.name)
            mapper.map_report(report, self.wagtail_report)
        return self.wagtail_report

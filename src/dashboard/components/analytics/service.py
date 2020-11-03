import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from components.utils.date_picker import filter_dataframe_by_date, get_default_end_date, get_default_start_date

from dateutil.parser import *
from dateutil.tz import *
import datetime
from datetime import date
import lib.analytics_api as analytics


class AnalyticsService():
    """
        AnalyticsService represents a provider to controls AnalyticsComponent data.
    """

    def __init__(self):
        # analytics view id
        self.view_id = "215248741"
        self.analytics_days_range = 30
        self.page_path = "ga:pagePath=@/testeopiniao/,ga:pagePath=@/opiniao/"
        self.load_data()

    def load_data(self):
        """
            reads the data stored by airflow on /tmp/votes_analytics.json.
            Also initializes analytics api client.
        """
        self.df = pd.DataFrame({})
        try:
            self.df = pd.read_json('/tmp/votes_analytics.json')
            self.analytics_client = analytics.initialize_analyticsreporting()
        except Exception as err:
            print(f"Error on analytics service: {err}")
            pass

    def get_analytics_users(self, query):
        if (query == {}):
            query = self.get_default_filter()
        response = analytics.get_report(self.analytics_client, query)
        return self.get_report_total_value(response)

    def get_date_filter(self, start_date, end_date):
        start_date = start_date.split('T')[0]
        end_date = end_date.split('T')[0]
        return {
            "reportRequests": [
                {
                    "viewId": self.view_id,
                    "dateRanges": {
                        "startDate": start_date,
                        "endDate": end_date
                    },
                    "metrics": [{
                        "expression": "ga:users",
                        "alias": "users",
                        "formattingType": "INTEGER"
                    }],
                    "dimensions": [{
                        "name": "ga:pagePath"
                    }],
                    "filtersExpression": self.page_path
                }
            ],
            "useResourceQuotas": False
        }

    def get_campaign_filter(self, campaign, start_date, end_date):
        start_date = start_date.split('T')[0]
        end_date = end_date.split('T')[0]
        return {
            "reportRequests": [
                {
                    "viewId": self.view_id,
                    "dateRanges": {
                        "startDate": start_date,
                        "endDate": end_date
                    },
                    "metrics": [{
                        "expression": "ga:users",
                        "alias": "users",
                        "formattingType": "INTEGER"
                    }],
                    "dimensions": [{
                        "name": "ga:pagePath"
                    },
                        {
                        "name": "ga:source"
                    }],
                    "filtersExpression": f"{self.page_path};ga:source=={campaign}"
                }
            ],
            "useResourceQuotas": False
        }

    def get_name_filter(self, campaign_name, start_date, end_date):
        start_date = start_date.split('T')[0]
        end_date = end_date.split('T')[0]
        return {
            "reportRequests": [
                {
                    "viewId": self.view_id,
                    "dateRanges": {
                        "startDate": start_date,
                        "endDate": end_date
                    },
                    "metrics": [{
                        "expression": "ga:users",
                        "alias": "users",
                        "formattingType": "INTEGER"
                    }],
                    "dimensions": [{
                        "name": "ga:pagePath"
                    },
                        {
                        "name": "ga:campaign"
                    }],
                    "filtersExpression": f"{self.page_path};ga:campaign=={campaign_name}"
                }
            ],
            "useResourceQuotas": False
        }

    def get_medium_filter(self, campaign_medium, start_date, end_date):
        start_date = start_date.split('T')[0]
        end_date = end_date.split('T')[0]
        return {
            "reportRequests": [
                {
                    "viewId": self.view_id,
                    "dateRanges": {
                        "startDate": start_date,
                        "endDate": end_date
                    },
                    "metrics": [{
                        "expression": "ga:users",
                        "alias": "users",
                        "formattingType": "INTEGER"
                    }],
                    "dimensions": [{
                        "name": "ga:pagePath"
                    },
                        {
                        "name": "ga:medium"
                    }],
                    "filtersExpression": f"{self.page_path};ga:medium=={campaign_medium}"
                }
            ],
            "useResourceQuotas": False
        }

    def get_report_total_value(self, reports):
        report = reports.get('reports')[0]
        if report:
            new_users = report.get('data').get('totals')[0].get('values')[0]
            return int(new_users)

    def filter_dataframe_by_date(self, df, start_date, end_date):
        return filter_dataframe_by_date(df, start_date, end_date)

    def get_default_end_date(self):
        return get_default_end_date()

    def get_default_start_date(self):
        return get_default_start_date()

    def filter_analytics_users_by_utm_source(self, df, campaign_source, start_date, end_date):
        utm_source_query = self.get_campaign_filter(
            campaign_source, start_date, end_date)
        return self.get_analytics_users(utm_source_query)

    def filter_analytics_users_by_utm_name(self, df, campaign_name, start_date, end_date):
        utm_name_query = self.get_name_filter(
            campaign_name, start_date, end_date)
        return self.get_analytics_users(utm_name_query)

    def filter_analytics_users_by_utm_medium(self, df, campaign_medium, start_date, end_date):
        utm_medium_query = self.get_medium_filter(
            campaign_medium, start_date, end_date)
        return self.get_analytics_users(utm_medium_query)

    def filter_analytics_users_by_date(self, start_date, end_date):
        date_query = self.get_date_filter(
            start_date, end_date)
        return self.get_analytics_users(date_query)

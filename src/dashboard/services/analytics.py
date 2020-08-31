import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

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
        self.df = pd.DataFrame({})
        # analytics view id
        self.view_id = "215248741"
        self.analytics_days_range = 30
        self.page_path = "ga:pagePath=@/testeopiniao/,ga:pagePath=@/opiniao/"
        self.prepare()

    def prepare(self):
        """
            reads the data stored by airflow on /tmp/votes_analytics_mautic.json.
            Also initializes analytics api client.
        """
        try:
            self.df = pd.read_json('/tmp/votes_analytics_mautic.json')
            self.analytics_client = analytics.initialize_analyticsreporting()
        except Exception as err:
            print(f"Error: {err}")

    def filter_by_analytics(self, _filter):
        if (_filter == {}):
            _filter = self.get_default_filter()
        analytics_users = self.get_analytics_new_users(_filter)
        return int(analytics_users)

    def get_default_filter(self):
        # start from datetime.now - self.analytics_days_range days
        startDate = (datetime.datetime.now(datetime.timezone.utc) -
                     datetime.timedelta(self.analytics_days_range)).strftime("%Y-%m-%d")
        # include today on report
        endDate = datetime.datetime.now(
            datetime.timezone.utc).strftime("%Y-%m-%d")
        return {
            "reportRequests": [
                {
                    "viewId": self.view_id,
                    "dateRanges": {
                        "startDate": startDate,
                        "endDate": endDate
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

    def get_date_filter(self, start_date, end_date):
        start_date = start_date.strftime("%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")
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

    def get_campaign_filter(self, campaign):
        # start from datetime.now - 60 days
        startDate = (datetime.datetime.now(datetime.timezone.utc) -
                     datetime.timedelta(self.analytics_days_range)).strftime("%Y-%m-%d")
        # include today on report
        endDate = datetime.datetime.now(
            datetime.timezone.utc).strftime("%Y-%m-%d")
        return {
            "reportRequests": [
                {
                    "viewId": self.view_id,
                    "dateRanges": {
                        "startDate": startDate,
                        "endDate": endDate
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

    def get_name_filter(self, campaign_name):
        # start from datetime.now - 60 days
        startDate = (datetime.datetime.now(datetime.timezone.utc) -
                     datetime.timedelta(self.analytics_days_range)).strftime("%Y-%m-%d")
        # include today on report
        endDate = datetime.datetime.now(
            datetime.timezone.utc).strftime("%Y-%m-%d")
        return {
            "reportRequests": [
                {
                    "viewId": self.view_id,
                    "dateRanges": {
                        "startDate": startDate,
                        "endDate": endDate
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

    def get_medium_filter(self, campaign_medium):
        # start from datetime.now - 60 days
        startDate = (datetime.datetime.now(datetime.timezone.utc) -
                     datetime.timedelta(self.analytics_days_range)).strftime("%Y-%m-%d")
        # include today on report
        endDate = datetime.datetime.now(
            datetime.timezone.utc).strftime("%Y-%m-%d")
        return {
            "reportRequests": [
                {
                    "viewId": self.view_id,
                    "dateRanges": {
                        "startDate": startDate,
                        "endDate": endDate
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

    def get_analytics_new_users(self, _filter):
        print("ANALYTICS_USERS")
        response = analytics.get_report(self.analytics_client, _filter)
        print(response)
        print("ANALYTICS_USERS")
        return self.parse_report(response)

    def parse_report(self, reports):
        report = reports.get('reports')[0]
        if report:
            new_users = report.get('data').get('totals')[0].get('values')[0]
            return new_users

    def dataframe_between_dates(self, df, first_day, last_day):
        if(first_day and last_day):
            partial_df = df[df['criado'].map(lambda x: parse(
                x).date() >= first_day and parse(x).date() <= last_day)]['email'].value_counts()
            return pd.DataFrame(partial_df)
        elif (first_day and not last_day):
            partial_df = df[df['criado'].map(
                lambda x: parse(x).date() < first_day)]
            return pd.DataFrame(partial_df)
        elif (last_day and not first_day):
            partial_df = df[df['criado'].map(
                lambda x: parse(x).date() > last_day)]
            return pd.DataFrame(partial_df)

    def set_filters_options(self, component, df=pd.DataFrame({})):
        if(df.empty):
            df = self.df
        df = df.groupby(['email',
                         'analytics_campaign',
                         'analytics_source',
                         'analytics_medium']) \
            .count().reset_index(level=0).reset_index(level=0) \
            .reset_index(level=0) \
            .reset_index(level=0) \
            .sort_values(by='criado', ascending=False)
        component.utm_source_options = df['analytics_source'].value_counts(
        ).keys()
        component.utm_medium_options = df['analytics_medium'].value_counts(
        ).keys()
        component.utm_campaign_options = df['analytics_campaign'].value_counts(
        ).keys()

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


class VotesService():
    """
        VotesService represents a object controls VotesComponent data.
    """

    def __init__(self):
        self.df = pd.DataFrame({})
        self.prepare()

    def prepare(self):
        """
            reads the data stored by airflow on /tmp/votes_analytics_mautic.json.
        """
        try:
            self.df = pd.read_json('/tmp/votes_analytics_mautic.json')
        except:
            pass

    def set_filters_options(self, component):
        component.utm_source_options = self.df['analytics_source'].value_counts(
        ).keys()
        component.utm_medium_options = self.df['analytics_medium'].value_counts(
        ).keys()
        component.utm_campaign_options = self.df['analytics_campaign'].value_counts(
        ).keys()

    def groupby(self, df):
        if(df.empty):
            df = self.df
        return df.groupby(['email',
                           'analytics_campaign',
                           'analytics_source',
                           'analytics_medium']) \
            .count().reset_index(level=0).reset_index(level=0) \
            .reset_index(level=0) \
            .reset_index(level=0) \
            .sort_values(by='criado', ascending=False)

    def filter_by_date(self, start_date, end_date):
        if(start_date and end_date):
            return self.dataframe_between_dates(
                self.df, datetime.datetime.fromisoformat(start_date).date(), datetime.datetime.fromisoformat(end_date).date())
        if(start_date):
            return self.dataframe_between_dates(
                self.df, datetime.datetime.fromisoformat(start_date).date(), None)
        if(end_date):
            return self.dataframe_between_dates(
                self.df, None, datetime.datetime.fromisoformat(end_date).date())

    def filter_by_utm(self, df, utm_name, utm_value):
        return df[df[utm_name] == utm_value]

    def dataframe_between_dates(self, df, first_day, last_day):
        if(first_day and last_day):
            partial_df = df[df['criado'].map(lambda x: parse(
                x).date() >= first_day and parse(x).date() <= last_day)]
            return pd.DataFrame(partial_df)
        elif (first_day and not last_day):
            partial_df = df[df['criado'].map(
                lambda x: parse(x).date() >= first_day)]
            return pd.DataFrame(partial_df)
        elif (last_day and not first_day):
            partial_df = df[df['criado'].map(
                lambda x: parse(x).date() <= last_day)]
            return pd.DataFrame(partial_df)
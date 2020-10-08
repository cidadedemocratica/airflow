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


class VotesService():
    """
        VotesService represents a object controls VotesComponent data.
    """

    def __init__(self):
        self.load_data()

    def load_data(self):
        """
            reads the data stored by airflow on /tmp/votes_analytics_mautic.json.
        """
        self.df = pd.DataFrame({})
        try:
            self.df = pd.read_json('/tmp/votes_analytics_mautic.json')
            self.df.mtc_email.fillna('-', inplace=True)
        except Exception as err:
            print(f"Error on votes service: {err}")

    def groupby(self, df):
        if(df.empty):
            df = self.df
        return df.groupby(['email']) \
            .count().reset_index(level=0) \
            .sort_values(by='criado', ascending=False)

    def filter_by_utm(self, df, utm_name, utm_value):
        if(utm_value and len(utm_value) >= 3):
            return df[df[utm_name] == utm_value]
        return df

    def filter_by_email(self, df, email):
        if(email == ['is_valid']):
            return df[(df.mtc_email != '-') | (df.email.str.contains('mautic@mail.com') == False)]
        return df

    def filter_dataframe_by_date(self, df, start_date, end_date):
        return filter_dataframe_by_date(df, start_date, end_date)

    def get_default_end_date(self):
        return get_default_end_date()

    def get_default_start_date(self):
        return get_default_start_date()

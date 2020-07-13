import dash
import dash_core_components as dcc
import dash_html_components as html
from comments import Comments
from votes import Votes
from analytics import Analytics
from dash.dependencies import Input, Output

from dateutil.parser import *
from dateutil.tz import *
import datetime
from datetime import date


class App():

    def __init__(self):
        self.votes = Votes()
        self.comments = Comments()
        self.analytics = Analytics()
        self.votes.read()
        self.comments.read()
        self.analytics.read()
        self.app = dash.Dash(
            __name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

    def create(self):
        self.app.layout = html.Div(style={'background-color': '#DBDDDF'}, children=[
            html.Div(style={'background': 'white', 'height': '5rem', 'fontSize': '3rem'},
                     children="Dashboard"),
            html.Div(style={"width": "90%", "margin": "30px auto", 'background-color': '#DBDDDF'}, children=[
                html.Div(style={}, children=[
                    self.analytics.get_html(),
                ]),
                html.Div(style={}, children=[
                    self.votes.get_html(),
                ]),
                self.comments.get_html()
            ])])

    def callbacks(self):
        @self.app.callback(
            Output("table_body", 'children'),
            [Input('_filter', 'value'), Input('participation', 'value')])
        def table_callback(_filter, participation):
            df = self.comments.df
            if(participation):
                df = df[df['participação'] >= int(participation) / 100]
            if(_filter in self.comments.order_options):
                df = df.sort_values(by=_filter, ascending=False)
                return self.comments.generate_table_body(df)
            return self.comments.generate_table_body(df)

        @self.app.callback(
            Output("analytics_filters", 'children'),
            [Input('analytics_campaign_source', 'value'),
             Input('analytics_campaign_name', 'value'),
             Input('analytics_campaign_medium', 'value'),
             Input('votes_by_date', 'start_date'),
             Input('votes_by_date', 'end_date'),
             ])
        def distribution_callback(analytics_campaign_source, analytics_campaign_name, analytics_campaign_medium, start_date, end_date):
            df = self.votes.df
            if(analytics_campaign_source and len(analytics_campaign_source) >= 3):
                df = df[df['analytics_source'] ==
                        analytics_campaign_source]

            if(analytics_campaign_medium and len(analytics_campaign_medium) >= 3):
                df = df[df['analytics_medium'] ==
                        analytics_campaign_medium]

            if(analytics_campaign_name and len(analytics_campaign_name) >= 3):
                df = df[df['analytics_campaign'] ==
                        analytics_campaign_name]

            if(start_date):
                df = self.votes.dataframe_between_dates(
                    self.votes.df, datetime.datetime.fromisoformat(start_date).date(), None)

            if(end_date):
                df = self.votes.dataframe_between_dates(
                    self.votes.df, None, datetime.datetime.fromisoformat(start_date).date())

            if(start_date and end_date):
                df = self.votes.dataframe_between_dates(
                    self.votes.df, datetime.datetime.fromisoformat(start_date).date(), datetime.datetime.fromisoformat(end_date).date())

            return self.votes.get_figure(df)

        @self.app.callback(
            Output("query_explorer_filters", 'children'),
            [Input('query_explorer_campaign_source', 'value'),
             Input('query_explorer_campaign_name', 'value'),
             Input('query_explorer_campaign_medium', 'value'),
             Input('query_explorer_by_date', 'start_date'),
             Input('query_explorer_by_date', 'end_date'),
             ])
        def distribution_callback(query_explorer_campaign_source, query_explorer_campaign_name, query_explorer_campaign_medium, start_date, end_date):
            _filter = None
            if(query_explorer_campaign_source and len(query_explorer_campaign_source) >= 3):
                self.analytics.set_campaign_filter(
                    query_explorer_campaign_source)

            return self.analytics.get_figure(self.analytics.df)

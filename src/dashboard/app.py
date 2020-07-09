import dash
import dash_core_components as dcc
import dash_html_components as html
from comments import Comments
from votes import Votes
from dash.dependencies import Input, Output


class App():

    def __init__(self):
        self.votes = Votes()
        self.comments = Comments()
        self.votes.read()
        self.comments.read()
        self.app = dash.Dash(
            __name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

    def create(self):
        self.app.layout = html.Div(style={'background-color': '#DBDDDF'}, children=[
            html.Div(style={'background': 'white', 'height': '5rem', 'fontSize': '3rem'},
                     children="Dashboard"),
            html.Div(style={"width": "90%", "margin": "30px auto", 'background-color': '#DBDDDF'}, children=[
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
             Input('analytics_campaign_medium', 'value')])
        def distribution_callback(analytics_campaign_source, analytics_campaign_name, analytics_campaign_medium):
            df = self.votes.df
            if(analytics_campaign_source and len(analytics_campaign_source) >= 3):
                print(df['analytics_source'])
                df = df[df['analytics_source'] ==
                        analytics_campaign_source]

            if(analytics_campaign_medium and len(analytics_campaign_medium) >= 3):
                print(df['analytics_medium'])
                df = df[df['analytics_medium'] ==
                        analytics_campaign_medium]

            if(analytics_campaign_name and len(analytics_campaign_name) >= 3):
                print(df['analytics_campaign'])
                df = df[df['analytics_campaign'] ==
                        analytics_campaign_name]
            return self.votes.get_figure(df)

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

# VIEW_ID = os.getenv("VIEW_ID")
VIEW_ID = "215248741"


class AnalyticsComponent():

    def __init__(self, app):
        self.app = app
        self.prepare()
        self.callbacks()

    def prepare(self):
        self.df = pd.read_json('/tmp/votes_analytics_mautic.json')
        self.analytics_client = analytics.initialize_analyticsreporting()
        self.set_default_filter()

    def render(self):
        return html.Div(className="row", children=[
            html.Div(className="col-12 mb-4", children=[
                html.Div(className="card shadow", children=[
                    html.Div(className="card-header", children=[
                        'Engajamento vs Aquisição (EJ)']),
                    html.Div(className="card-body", children=[
                        html.Div(style={"display": "flex"}, children=[
                            self._get_filters(self.df),
                            html.Div(id="query_explorer_filters",
                                     style={"flexGrow": 1, "width": "60%"}, children=[
                                         self.get_figure(self.df)
                                     ])
                        ])
                    ])
                ])
            ])
        ])

    def get_figure(self, new_df):
        df = None
        try:
            new_df.head(1)
            df = new_df
        except:
            df = self.df
        fig = go.Figure(layout={'title': {'text': '', 'x': 0.5,
                                          'font': {'size': 16, 'color': '#ff3e72', 'family': 'Times New Roman'}},
                                'xaxis': {'visible': False},
                                'yaxis': {'visible': False},
                                'plot_bgcolor': "#ffffff",
                                'legend': {
            'font': {'size': 15, 'color': '#000'},
                                    'y': 0.8
        },
            'annotations': [
            {
                'x': '-50',
                'y': '50',
                'text': f'<b>{round((self.ej_users/self.analytics_users) * 100,2) }%</b>',
                'font': {'color': '#fff', 'size': 15},
                'align': 'center',
                'showarrow': False
            },
            {
                'x': '-50',
                'y': '50',
                'yshift': 90,
                'text': f'<b>{self.analytics_users} visitantes</b>',
                'font': {'color': '#fff', 'size': 15},
                'showarrow': False
            }
        ]
        }
        )

        fig.add_trace(go.Scatter(
            x=[-50], y=[50],
            mode='markers',
            marker=dict(
                size=[300],
                color='#30bfd3',
                sizeref=1.1,
            ),
            name="Visitas na pagina da conversa (/opiniao)")
        )

        fig.add_trace(go.Scatter(
            x=[-50], y=[50],
            mode='markers',
            marker=dict(
                size=[(300 / self.analytics_users) * self.ej_users],
                color='#C4F2F4',
                sizeref=1.1,
                maxdisplayed=1),
            name="Visitas que participaram da conversa",
        )
        )
        return html.Div(children=[
            dcc.Graph(figure=fig)
        ])

    def get_analytics_report(self, _filter):
        if (_filter == None):
            _filter = self.get_default_filter()
        analytics_users = self._get_analytics_new_users(_filter)
        return int(analytics_users)

    def get_default_filter(self):
        # start from datetime.now - 60 days
        startDate = (datetime.datetime.now(datetime.timezone.utc) -
                     datetime.timedelta(days=90)).strftime("%Y-%m-%d")
        # include today on report
        endDate = datetime.datetime.now(
            datetime.timezone.utc).strftime("%Y-%m-%d")
        return {
            "reportRequests": [
                {
                    "viewId": VIEW_ID,
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
                    "filtersExpression": f"ga:pagePath==/opiniao/"
                }
            ],
            "useResourceQuotas": False
        }

    def set_default_filter(self):
        self.ej_users = len(self.df['email'].value_counts())
        self.analytics_users = self.get_analytics_report(None)

    def set_campaign_source_filter(self, campaign):
        analytics_filter = self.filter_by_campaign(campaign)
        self.analytics_users = self.get_analytics_report(analytics_filter)

        self.ej_users = int(
            len(self.df[self.df['analytics_source']
                        == campaign]['email'].value_counts()))

    def set_campaign_name_filter(self, campaign):
        analytics_filter = self.filter_by_name(campaign)
        self.analytics_users = self.get_analytics_report(analytics_filter)

        self.ej_users = int(
            len(self.df[self.df['analytics_campaign']
                        == campaign]['email'].value_counts()))

    def set_campaign_medium_filter(self, campaign):
        analytics_filter = self.filter_by_medium(campaign)
        self.analytics_users = self.get_analytics_report(analytics_filter)

        self.ej_users = int(
            len(self.df[self.df['analytics_medium']
                        == campaign]['email'].value_counts()))

    def set_campaign_date_range_filter(self, start_date, end_date):
        analytics_filter = self.filter_by_date(start_date, end_date)
        self.analytics_users = self.get_analytics_report(analytics_filter)

        self.ej_users = int(len(self.dataframe_between_dates(
            self.df, start_date, end_date)))

    def filter_by_date(self, start_date, end_date):
        start_date = start_date.strftime("%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")
        return {
            "reportRequests": [
                {
                    "viewId": VIEW_ID,
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
                    "filtersExpression": f"ga:pagePath==/opiniao/"
                }
            ],
            "useResourceQuotas": False
        }

    def filter_by_campaign(self, campaign):
        # start from datetime.now - 60 days
        startDate = (datetime.datetime.now(datetime.timezone.utc) -
                     datetime.timedelta(days=90)).strftime("%Y-%m-%d")
        # include today on report
        endDate = datetime.datetime.now(
            datetime.timezone.utc).strftime("%Y-%m-%d")
        return {
            "reportRequests": [
                {
                    "viewId": VIEW_ID,
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
                    "filtersExpression": f"ga:pagePath==/opiniao/;ga:source=={campaign}"
                }
            ],
            "useResourceQuotas": False
        }

    def filter_by_name(self, campaign_name):
        # start from datetime.now - 60 days
        startDate = (datetime.datetime.now(datetime.timezone.utc) -
                     datetime.timedelta(days=90)).strftime("%Y-%m-%d")
        # include today on report
        endDate = datetime.datetime.now(
            datetime.timezone.utc).strftime("%Y-%m-%d")
        return {
            "reportRequests": [
                {
                    "viewId": VIEW_ID,
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
                    "filtersExpression": f"ga:pagePath==/opiniao/;ga:campaign=={campaign_name}"
                }
            ],
            "useResourceQuotas": False
        }

    def filter_by_medium(self, campaign_medium):
        # start from datetime.now - 60 days
        startDate = (datetime.datetime.now(datetime.timezone.utc) -
                     datetime.timedelta(days=90)).strftime("%Y-%m-%d")
        # include today on report
        endDate = datetime.datetime.now(
            datetime.timezone.utc).strftime("%Y-%m-%d")
        return {
            "reportRequests": [
                {
                    "viewId": VIEW_ID,
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
                    "filtersExpression": f"ga:pagePath==/opiniao/;ga:medium=={campaign_medium}"
                }
            ],
            "useResourceQuotas": False
        }

    def _get_analytics_new_users(self, _filter):
        response = analytics.get_report(self.analytics_client, _filter)
        return self.parse_report(response)

    def parse_report(self, reports):
        report = reports.get('reports')[0]
        if report:
            new_users = report.get('data').get('totals')[0].get('values')[0]
            return new_users

    def _get_filters(self, new_df):
        self.set_filters_options(new_df)
        return html.Div(style={"flexGrow": "2"}, children=[
            html.Div(style={'width': '95%', 'margin': 'auto', 'marginTop': '20px'}, children=[
                html.Div(children=[html.Div(style={'display': 'flex', 'marginTop': '10px', 'alignItems': 'center'}, children=[
                    html.Span(style={"marginRight": 8, "fontWeight": "bold"},
                              children="utm_source:"),
                    dcc.Dropdown(
                        id='query_explorer_campaign_source',
                        options=[{'label': i, 'value': i}
                                 for i in self.utm_source_options],
                        value='',
                        style={"flexGrow": 1}
                    ),
                ])
                ]),
                html.Div(children=[html.Div(style={'display': 'flex', 'marginTop': '10px', 'alignItems': 'center'}, children=[
                    html.Span(style={"marginRight": 8, "fontWeight": "bold"},
                              children="utm_medium:"),
                    dcc.Dropdown(
                        id='query_explorer_campaign_medium',
                        options=[{'label': i, 'value': i}
                                 for i in self.utm_medium_options],
                        value='',
                        style={"flexGrow": 1}
                    ),
                ])
                ]),
                html.Div(children=[html.Div(style={'display': 'flex', 'marginTop': '10px', 'alignItems': 'center'}, children=[
                    html.Span(style={"marginRight": 8, "fontWeight": "bold"},
                              children="utm_campaign:"),
                    dcc.Dropdown(
                        id='query_explorer_campaign_name',
                        options=[{'label': i, 'value': i}
                                 for i in self.utm_campaign_options],
                        value='',
                        style={"flexGrow": 1}
                    ),
                ])
                ]),
                html.Div(children=[html.Div(style={'display': 'flex', 'marginTop': '10px', 'alignItems': 'center'}, children=[
                    html.Span(style={"marginRight": 8, "fontWeight": "bold"},
                              children="Período:"),
                    dcc.DatePickerRange(
                        id='query_explorer_by_date',
                        style={"flexGrow": 1},
                    ),
                ])
                ]),
            ])
        ],
        )

    def set_filters_options(self, new_df):
        df = None
        try:
            new_df.head(1)
            df = new_df
        except:
            df = self.df
        df = df.groupby(['email',
                         'analytics_campaign',
                         'analytics_source',
                         'analytics_medium']) \
            .count().reset_index(level=0).reset_index(level=0) \
            .reset_index(level=0) \
            .reset_index(level=0) \
            .sort_values(by='criado', ascending=False)
        self.utm_source_options = df['analytics_source'].value_counts(
        ).keys()
        self.utm_medium_options = df['analytics_medium'].value_counts(
        ).keys()
        self.utm_campaign_options = df['analytics_campaign'].value_counts(
        ).keys()

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

    def callbacks(self):
        @self.app.callback(
            Output("query_explorer_filters", 'children'),
            [Input('query_explorer_campaign_source', 'value'),
                Input('query_explorer_campaign_name', 'value'),
                Input('query_explorer_campaign_medium', 'value'),
                Input('query_explorer_by_date', 'start_date'),
                Input('query_explorer_by_date', 'end_date'),
             ])
        def query_explorer_callback(query_explorer_campaign_source,
                                    query_explorer_campaign_name,
                                    query_explorer_campaign_medium,
                                    start_date,
                                    end_date):
            _filter = None
            if(query_explorer_campaign_source and len(query_explorer_campaign_source) >= 3):
                self.set_campaign_source_filter(
                    query_explorer_campaign_source)

            elif(query_explorer_campaign_name and len(query_explorer_campaign_name) >= 3):
                self.set_campaign_name_filter(
                    query_explorer_campaign_name)

            elif(query_explorer_campaign_medium and len(query_explorer_campaign_medium) >= 3):
                self.set_campaign_medium_filter(
                    query_explorer_campaign_medium)

            elif(start_date and end_date):
                self.set_campaign_date_range_filter(datetime.datetime.fromisoformat(start_date).date(),
                                                    datetime.datetime.fromisoformat(end_date).date())

            else:
                self.set_default_filter()
            return self.get_figure(self.df)

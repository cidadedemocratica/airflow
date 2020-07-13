import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import dash_html_components as html
import dash_core_components as dcc

from dateutil.parser import *
from dateutil.tz import *
import datetime
from datetime import date
import analytics_api as analytics

# VIEW_ID = os.getenv("VIEW_ID")
VIEW_ID = "215248741"


class Analytics():

    def read(self):
        self.df = pd.read_json('/tmp/airflow/votes_analytics_mautic.json')
        self.analytics_client = analytics.initialize_analyticsreporting()
        self.set_default_filter()

    def get_html(self):
        return html.Div(style={'background-color': 'white', 'marginTop': '15px'},
                        children=[
            html.Div(style={"textAlign": "center", "backgroundColor": "#042a46", "color": "white", "height": "40px"},
                     children=[
                         html.Div(style={"position": "relative", "top": "20%"},
                                  children=['Engajamento vs Aquisição (EJ)'])
            ]
            ),
            html.Div(
                style={'display': 'flex'},
                children=[
                    self._get_filters(self.df),
                    html.Div(
                        style={'flexGrow': 1, 'width': '60%',
                               'background-color': 'white'},
                        children=[
                            html.Div(id="query_explorer_filters",
                                     children=[self.get_figure(self.df)]
                                     )
                        ]
                    ),
                ]
            )
        ])

    def get_figure(self, new_df):
        df = None
        try:
            new_df.head(1)
            df = new_df
        except:
            df = self.df
        fig = go.Figure(layout={'title': {'text': '', 'x': 0.5,
                                          'font': {'size': 20, 'color': '#ff3e72', 'family': 'Times New Roman'}},
                                'xaxis': {'visible': False},
                                'yaxis': {'visible': False},
                                'plot_bgcolor': "#ffffff",
                                'width': 500,
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
                size=[(300 - self.analytics_users) + self.analytics_users],
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
        return html.Div(style={'width': '90%', 'margin': '20px auto'}, children=[
            dcc.Graph(figure=fig)
        ])

    def get_analytics_report(self, _filter):
        if (_filter == None):
            _filter = self.get_default_filter()
        analytics_users = self._get_analytics_new_users(_filter)
        print(_filter)
        print(int(analytics_users))
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
                        "expression": "ga:newUsers",
                        "alias": "newUsers",
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

    def set_campaign_filter(self, campaign):
        analytics_filter = self.filter_by_campaign(campaign)
        self.analytics_users = self.get_analytics_report(analytics_filter)

        self.ej_users = int(
            len(self.df[self.df['analytics_source']
                        == campaign]['email'].value_counts()))
        print("ej users")
        print(self.ej_users)
        print(self.analytics_users)
        print("ej users")

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
                        "expression": "ga:newUsers",
                        "alias": "newUsers",
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

    def _get_analytics_new_users(self, _filter):
        response = analytics.get_report(self.analytics_client, _filter)
        return self.parse_report(response)

    def parse_report(self, reports):
        report = reports.get('reports')[0]
        if report:
            new_users = report.get('data').get('totals')[0].get('values')[0]
            return new_users

    def _get_filters(self, new_df):
        self.groupData(new_df)
        return html.Div(style={"flexGrow": "2"}, children=[
            html.Div(children=[html.Div(style={'display': 'flex'}, children=[
                html.Span(style={"marginRight": 8},
                          children="Fonte da campanha (utm_source):"),
                dcc.Dropdown(
                        id='query_explorer_campaign_source',
                        options=[{'label': i, 'value': i}
                                 for i in self.utm_source_options],
                        value='',
                        style={"flexGrow": 1}
                        ),
            ])
            ]),
            html.Div(style={'width': '90%', 'margin': 'auto', 'marginTop': '20px'},
                     children=[html.Div(style={'display': 'flex'}, children=[
                         html.Span(style={"marginRight": 8},
                                   children="Meio da campanha (utm_medium):"),
                         dcc.Dropdown(
                             id='query_explorer_campaign_medium',
                             options=[{'label': i, 'value': i}
                                      for i in self.utm_medium_options],
                             value='',
                             style={"flexGrow": 1}
                         ),
                     ])
            ]),
            html.Div(style={'width': '90%', 'margin': 'auto', 'marginTop': '20px'},
                     children=[html.Div(style={'display': 'flex'}, children=[
                         html.Span(style={"marginRight": 8},
                                   children="Nome da campanha (utm_campaign):"),
                         dcc.Dropdown(
                             id='query_explorer_campaign_name',
                             options=[{'label': i, 'value': i}
                                      for i in self.utm_campaign_options],
                             value='',
                             style={"flexGrow": 1}
                         ),
                     ])
            ]),
            html.Div(style={'width': '90%', 'margin': 'auto', 'marginTop': '20px'},
                     children=[html.Div(style={'display': 'flex'}, children=[
                         html.Span(style={"marginRight": 8},
                                   children="Período"),
                         dcc.DatePickerRange(
                             id='query_explorer_by_date',
                             style={"flexGrow": 1},
                         ),
                     ])
            ]),
        ],
        )

    def groupData(self, new_df):
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
        return df

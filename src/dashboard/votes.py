import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import dash_html_components as html
import dash_core_components as dcc
from mautic_sdk import MauticSdk


class Votes():

    def read(self):
        df = pd.read_json('/tmp/airflow/votes_analytics_mautic.json')
        self.df = df.groupby(['email',
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

    def get_figure(self, new_df):
        df = None
        try:
            new_df.head(1)
            df = new_df
        except:
            df = self.df
        fig = go.Figure(
            data=go.Box(name='Distribuição dos votos',
                        y=df['criado'], boxpoints='all',
                        marker_color='#30bfd3'),
            layout={'title': {'text': '', 'x': 0.5, 'font': {'size': 20, 'color': '#ff3e72', 'family': 'Times New Roman'}}, 'legend': {'font': {'size': 15, 'color': '#000'}, 'y': 0.8}, })
        fig.update_layout(yaxis_zeroline=False)
        return html.Div(children=[dcc.Graph(figure=fig)])

    def get_html(self, new_df=None):

        return html.Div(
            style={'backgroundColor': 'white'},
            children=[
                html.Div(
                    style={"textAlign": "center",
                           "backgroundColor": "#042a46",
                           "color": "white", "height": "40px"},
                    children=[html.Div(
                        style={"position": "relative",
                               "top": "20%"},
                        children=['Aquisição Qualificada'])]
                ),
                html.Div(
                    children=[
                        self._get_filters(),
                        html.Div(
                            style={'flexGrow': 1,
                                   'background-color': 'white'},
                            children=[
                                html.Div(id="analytics_filters",
                                         children=[self.get_figure(new_df)]
                                         )
                            ]
                        ),
                    ]
                )
            ])

    def _get_filters(self):
        return html.Div(children=[
            html.Div(style={'width': '90%', 'margin': 'auto', 'marginTop': '20px'},
                     children=[html.Div(style={'display': 'flex'}, children=[
                         html.Span(style={"marginRight": 8},
                                   children="Fonte da campanha (utm_source):"),
                         dcc.Dropdown(
                             id='analytics_campaign_source',
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
                             id='analytics_campaign_medium',
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
                             id='analytics_campaign_name',
                             options=[{'label': i, 'value': i}
                                      for i in self.utm_campaign_options],
                             value='',
                             style={"flexGrow": 1}
                         ),
                     ])
            ]),
        ],
        )

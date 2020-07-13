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


class Votes():

    def read(self):
        self.df = pd.read_json('/tmp/airflow/votes_analytics_mautic.json')

    def get_figure(self, new_df):
        df = None
        try:
            new_df.head(1)
            df = new_df
        except:
            df = self.df
        df = self.groupData(new_df)
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
                    style={'display': 'flex'},
                    children=[
                        self._get_filters(new_df),
                        html.Div(
                            style={'flexGrow': 1, 'width': '50%',
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

    def _get_filters(self, new_df):
        self.groupData(new_df)
        return html.Div(style={"flexGrow": "2"}, children=[
            html.Div(children=[html.Div(style={'display': 'flex'}, children=[
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
            html.Div(style={'width': '90%', 'margin': 'auto', 'marginTop': '20px'},
                     children=[html.Div(style={'display': 'flex'}, children=[
                         html.Span(style={"marginRight": 8},
                                   children="Período"),
                         dcc.DatePickerRange(
                             id='votes_by_date',
                             style={"flexGrow": 1},
                         ),
                     ])
            ]),
        ],
        )

    def dataframe_between_dates(self, df, first_day, last_day):
        if(first_day and last_day):
            partial_df = df[df['criado'].map(lambda x: parse(
                x).date() >= first_day and parse(x).date() <= last_day)]
            return pd.DataFrame(partial_df)
        elif (first_day and not last_day):
            partial_df = df[df['criado'].map(
                lambda x: parse(x).date() < first_day)]
            return pd.DataFrame(partial_df)
        elif (last_day and not first_day):
            partial_df = df[df['criado'].map(
                lambda x: parse(x).date() > last_day)]
            return pd.DataFrame(partial_df)

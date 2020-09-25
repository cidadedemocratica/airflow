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
from services.votes import VotesService
from components.utils.export import ExportsComponent


class VotesComponent():
    """
        VotesComponent represents a Dash component. This component will
        show a distribution Chart with some analytics filters.
    """

    def __init__(self, app):
        self.app = app
        self.service = VotesService()
        self.export_component = ExportsComponent("votes")
        self.prepare()

    def prepare(self):
        try:
            self.df = self.service.df
            self.utm_source_options = []
            self.utm_medium_options = []
            self.utm_campaign_options = []
            self.register_callbacks()
            self.service.set_filters_options(self)
        except Exception as err:
            print(err)

    def get_figure(self):
        df = self.service.groupby(self.df)
        fig = go.Figure(
            data=go.Box(name='Distribuição dos votos',
                        y=df['criado'], boxpoints='all',
                        marker_color='#30bfd3'),
            layout={
                'title': {'text': '', 'x': 0.5, 'font':
                          {'size': 20, 'color': '#ff3e72',
                                  'family': 'Times New Roman'}
                          },
                'legend': {'font': {'size': 15, 'color': '#000'}, 'y': 0.8}
            }
        )
        fig.update_layout(yaxis_zeroline=False)
        return html.Div(children=[dcc.Graph(figure=fig)])

    def render(self):
        if(not self.df.empty):
            return html.Div(className="row", children=[
                html.Div(className="col-12 mb-4", children=[
                    html.Div(className="card shadow", children=[
                        html.Div(className="card-header", children=[
                            'Aquisição Qualificada']),
                        html.Div(className="card-body", children=[
                            html.Div(style={"display": "flex", "width": "90%"}, children=[
                                html.Div(style={"flexGrow": "1"}, children=[
                                    self.get_filters_ui(),
                                    html.Hr(),
                                    self.export_component.render(),
                                ]),
                                dcc.Loading(id="votes_loader", type="default", color="#30bfd3", children=[
                                    html.Div(id="votes_filters",
                                             style={"flexGrow": 1, "width": "60%"}, children=[
                                                 self.get_figure()
                                             ])
                                ])
                            ])
                        ])
                    ])
                ])
            ])
        return html.Div(className="row", children=[
            html.Div(className="col-12 mb-4", children=[
                html.Div(className="card shadow", children=[
                    html.Div(className="card-header", children=[
                        'Aquisição Qualificada']),
                    html.Div(className="card-body",
                             children=["Não há dados para apresentar"])
                ])
            ])
        ])

    def get_filters_ui(self):
        self.service.set_filters_options(self)
        return html.Div(children=[
            html.Div(style={'width': '95%', 'margin': 'auto', 'marginTop': '20px'}, children=[
                html.Div(children=[html.Div(style={'display': 'flex', 'marginTop': '10px', 'alignItems': 'center'}, children=[
                    html.Span(style={"marginRight": 8, "fontWeight": "bold"},
                              children="utm_source:"),
                    dcc.Dropdown(
                        id='analytics_campaign_source',
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
                        id='analytics_campaign_medium',
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
                        id='analytics_campaign_name',
                        options=[{'label': i, 'value': i}
                                 for i in self.utm_campaign_options],
                        value='',
                        style={"flexGrow": 1}
                    ),
                ])
                ]),
                html.Div(children=[html.Div(style={'display': 'flex', 'marginTop': '10px', 'alignItems': 'center'}, children=[
                    html.Span(style={"marginRight": 8, "fontWeight": "bold"},
                              children="emails válidos?: "),
                    dcc.Checklist(
                        id='email',
                        options=[
                            {'label':  '', 'value': 'is_valid'}],
                        value=['is_valid'],
                        style={"flexGrow": 1}
                    ),
                ])
                ]),
                html.Div(children=[html.Div(style={'display': 'flex', 'marginTop': '10px'}, children=[
                    html.Span(style={"marginRight": 8, "fontWeight": "bold"},
                              children="Período"),
                    dcc.DatePickerRange(
                        id='votes_by_date',
                        clearable=True,
                        style={"flexGrow": 1},
                    ),
                ])
                ]),
            ]),
        ],
        )

    def register_callbacks(self):
        if(not self.df.empty):
            @self.app.callback(
                Output("votes_download_export", 'href'),
                [Input('votes_exports_df', 'n_clicks')]
            )
            def export_callback(export_df):
                return self.export_component.export(self.df)

            @self.app.callback(
                Output("votes_loader", 'children'),
                [Input('analytics_campaign_source', 'value'),
                    Input('analytics_campaign_name', 'value'),
                    Input('analytics_campaign_medium', 'value'),
                    Input('email', 'value'),
                    Input('votes_by_date', 'start_date'),
                    Input('votes_by_date', 'end_date'),
                    Input('app_reload', 'n_clicks'),
                 ])
            def distribution_callback(analytics_campaign_source, analytics_campaign_name, analytics_campaign_medium, email, start_date, end_date, app_reload):
                if(app_reload != 0):
                    self.service.load_data()
                    self.df = self.service.df
                self.df = self.service.df
                if(analytics_campaign_source and len(analytics_campaign_source) >= 3):
                    self.df = self.service.filter_by_utm(
                        self.df, 'analytics_source', analytics_campaign_source)
                elif(analytics_campaign_medium and len(analytics_campaign_medium) >= 3):
                    self.df = self.service.filter_by_utm(
                        self.df, 'analytics_medium', analytics_campaign_medium)
                elif(analytics_campaign_name and len(analytics_campaign_name) >= 3):
                    self.df = self.service.filter_by_utm(
                        self.df, 'analytics_campaign', analytics_campaign_name)
                elif(email == ['is_valid']):
                    self.df = self.service.filter_by_email(self.df)
                elif(start_date or end_date):
                    self.df = self.service.filter_by_date(
                        start_date, end_date)

                return self.get_figure()

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
from components.votes.service import VotesService
from components.utils.export import ExportsComponent
from components.votes.filters import FiltersComponent
from components.utils.date_picker import *


class VotesComponent():
    """
        VotesComponent represents a Dash component. This component will
        show a distribution Chart with some analytics filters.
    """

    def __init__(self, app):
        self.app = app
        self.service = VotesService()
        self.df = self.service.df
        self.export_component = ExportsComponent(
            "votes", self.app, self.df)
        self.filters_component = FiltersComponent(
            self.service, app, self, self.export_component)

    def get_figure(self):
        if(self.df.empty):
            return html.Div(children=[html.Span("Não há dados para apresentar")])

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
        return html.Div(className="row", children=[
            html.Div(className="col-12 mb-4", children=[
                html.Div(className="card shadow", children=[
                    html.Div(className="card-header", children=[
                        'Aquisição Qualificada']),
                    html.Div(className="card-body", children=[
                        html.Div(style={"display": "flex", "width": "90%"}, children=[
                            html.Div(style={"flexGrow": "1"}, children=[
                                self.filters_component.render(),
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

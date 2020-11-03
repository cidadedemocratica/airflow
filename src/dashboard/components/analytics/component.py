import datetime
import urllib.parse
from datetime import date

import pandas as pd
from dateutil.parser import *
from dateutil.tz import *

import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from components.utils.export import ExportsComponent
from components.analytics.service import AnalyticsService
from components.analytics.filters import FiltersComponent


class AnalyticsComponent():
    """
        AnalyticsComponent represents a Dash component. This component will
        show a bubble Chart with some analytics filters.
    """

    def __init__(self, app):
        self.prepare(app)

    def prepare(self, app):
        self.app = app
        self.ej_users_count = 1
        self.analytics_users_count = 1
        self.filters_component = FiltersComponent(self.app, self.get_figure)
        self.export_component = ExportsComponent(
            "analytics", app, self.filters_component)

    def render(self):
        """
            Main entrypoint to create a Dash visualization.
            render will show a plotly figure and the figure's filters.
        """
        return html.Div(className="row", children=[
            html.Div(className="col-12 mb-4", children=[
                html.Div(className="card shadow", children=[
                     html.Div(className="card-header", children=[
                        html.Div(children=[
                            html.Span("Engajamento vs Aquisição", style={
                                "marginRight": 4}),
                            html.I(className="fa fa-info-circle",
                                   id='votes-component-title')
                        ]),
                        dbc.Tooltip(
                            'Visualização que permite correlacionar a quantidade de acessos à pagina de coleta '
                            'em relação à porcentagem de participantes na conversa. Representa quão eficiente '
                            'é a EJ no processo de potencializar a aquisição de novos usuários.',
                            target='votes-component-title')
                        ]),
                     html.Div(className="card-body", children=[
                         html.Div(style={"display": "flex", "width": "90%"}, children=[
                             html.Div(style={"flexGrow": "1"}, children=[
                                 self.filters_component.render(),
                                 html.Hr(),
                                 self.export_component.render(),
                             ]),
                             dcc.Loading(id="analytics_loader", type="default", color="#30bfd3", children=[
                                 html.Div(id="analytics_filters",
                                          style={"flexGrow": 1, "width": "60%"}, children=[
                                             self.get_figure()
                                          ])
                             ])
                         ])
                     ])
                     ])
            ])
        ])

    def get_figure(self, df=pd.DataFrame({})):

        if(df.empty):
            return html.Div(children=[html.Span("Não há dados para apresentar")])

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
                'text': f'<b>{self.aquisition_percentage(df)}%</b>',
                'font': {'color': '#fff', 'size': 15},
                'align': 'center',
                'showarrow': False
            },
            {
                'x': '-50',
                'y': '50',
                'yshift': 90,
                'text': f'<b>{df.loc[0].analytics_users} visitantes</b>',
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
                size=[self.engagement_buble_size(df)],
                color='#C4F2F4',
                sizeref=1.1,
                maxdisplayed=1),
            name="Visitas que participaram da conversa",
        )
        )
        return html.Div(children=[
            dcc.Loading(
                id="loading-2",
                children=[html.Div([html.Div(id="loading-output-2")])],
                type="circle",
            ),
            dcc.Graph(figure=fig)
        ])

    def aquisition_percentage(self, df):
        analytics_users = df.loc[0].analytics_users
        ej_users = df.loc[0].ej_users
        if(analytics_users == 0):
            return 0.0
        return round((ej_users/analytics_users) * 100, 2)

    def engagement_buble_size(self, df):
        analytics_users = df.loc[0].analytics_users
        ej_users = df.loc[0].ej_users
        if(analytics_users == 0):
            return (300 / 1) * ej_users
        return (300 / analytics_users) * ej_users

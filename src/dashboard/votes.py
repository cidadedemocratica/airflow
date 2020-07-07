import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import dash_html_components as html
import dash_core_components as dcc
from mautic_sdk import MauticSdk


class Votes():

    def read(self):
        df = pd.read_json('/tmp/airflow/votes.json')
        self.df = df.groupby('email').count().reset_index(
            level=0).sort_values(by='criado', ascending=False)

    def _get_figure(self):
        fig = go.Figure(
            data=go.Box(name='Distribuição dos votos',
                        y=self.df['criado'], boxpoints='all',
                        marker_color='#30bfd3'),
            layout={'title': {'text': '', 'x': 0.5, 'font': {'size': 20, 'color': '#ff3e72', 'family': 'Times New Roman'}}, 'legend': {'font': {'size': 15, 'color': '#000'}, 'y': 0.8}, })
        fig.update_layout(yaxis_zeroline=False)
        return fig

    def get_html(self):
        return html.Div(
            style={'width': '49%'},
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
                    children=[html.Div(
                        style={'flexGrow': 1, 'background-color': 'white'},
                        children=[dcc.Graph(figure=self._get_figure())]),
                    ]
                )
            ])

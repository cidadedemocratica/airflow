import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import dash_html_components as html
import dash_core_components as dcc
from mautic_sdk import MauticSdk


class Votes():

    def __init__(self):
        self.read_ej_votes()

    def compile_data(self):
        self.df.rename(columns={'criado': 'votos'}, inplace=True)
        mautic_sdk = MauticSdk()
        for ej_email in self.df['email']:
            mautic_email = mautic_sdk.get_contact_email(ej_email)
            print(mautic_email)
            self.df.loc[self.df['email'] == ej_email,
                        'mautic_email'] = mautic_email
        self.df.fillna("empty", inplace=True)
        self.df.to_csv('/tmp/airflow/ej_mautic.json')

    def get_data(self, force=False):
        if(force):
            self.compile_data()
            self.df = pd.read_csv('/tmp/airflow/ej_mautic.json')
            return
        try:
            self.df = pd.read_csv('/tmp/airflow/ej_mautic.json')
        except:
            self.compile_data()

    def read_ej_votes(self):
        try:
            self.df = pd.read_csv('/tmp/airflow/ej_mautic.json')
        except:
            votes_df = pd.read_json('/tmp/airflow/ej_only.json')
            tmp = votes_df.groupby(['email']).count().reset_index(
                level=0).reset_index(level=0)
            top_50_voters_df = pd.DataFrame(tmp, columns=['criado', 'email'])
            top_50_voters_df.rename(columns={'criado': 'votos'}, inplace=True)
            top_50_voters_df.sort_values(
                by='votos', inplace=True, ascending=False)
            self.df = pd.DataFrame(top_50_voters_df)

    def _get_figure(self):
        fig = go.Figure(
            data=go.Box(name='Distribuição dos votos',
                        y=self.df['votos'], boxpoints='all',
                        marker_color='#30bfd3'),
            layout={'title': {'text': '', 'x': 0.5, 'font': {'size': 20, 'color': '#ff3e72', 'family': 'Times New Roman'}}, 'legend': {'font': {'size': 15, 'color': '#000'}, 'y': 0.8}, })
        df = self.df[
            (self.df['mautic_email'] != 'empty') &
            (self.df['mautic_email'] != 'ricabras@gmail.com') &
            (self.df['mautic_email'] != 'admin@mail.com') &
            (self.df['mautic_email']
             != 'ricardo@cidadedemocratica.org.br')
        ]
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

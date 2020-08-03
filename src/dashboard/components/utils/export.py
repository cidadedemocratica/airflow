import urllib.parse

import pandas as pd
from dateutil.parser import *
from dateutil.tz import *

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output


class ExportsComponent():

    def __init__(self, id_prefix):
        self.id_prefix = id_prefix

    def render(self):
        return html.Div(style={'marginTop': '10px'}, children=[
            html.Button(
                'Exportar', id=f"{self.id_prefix}_exports_df", n_clicks=0),
            html.Div(children=[
                html.A('Clique aqui para baixar', href='', id=f'{self.id_prefix}_download_export',
                       download='ej-raw-data.csv', target="_blank")
            ]),
        ])

    def export(self, df):
        dataAsCSV = df.to_csv()
        urlToDownload = "data:text/csv;charset=utf-8," + \
            urllib.parse.quote(dataAsCSV)
        return urlToDownload

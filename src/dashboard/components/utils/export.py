import urllib.parse

import pandas as pd
from dateutil.parser import *
from dateutil.tz import *

import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output


class ExportsComponent():

    def __init__(self, id_prefix, app, filters_component):
        self.id_prefix = id_prefix
        self.app = app
        self.filters_component = filters_component
        self.data_link_display = 'none'
        if(not self.filters_component.get_data_to_export().empty):
            self.add_callbacks()

    def render(self):
        return html.Div(style={'marginTop': '10px'}, children=[
            html.Button(className='dash-icon with-text', id=f"exporting_{self.id_prefix}", n_clicks=0, children=[
                html.Div(children=[
                        html.I(className='fa fa-2x fa-download'),
                        ]),
                html.Div(children=[
                    html.Span('Exportar como csv')
                ])
            ]),
            dcc.Loading(id=f"{self.id_prefix}_exporting_loader", type="default", color="#30bfd3", children=[
                html.Div(id=f'export_{self.id_prefix}_data', children=[
                    html.A('data.csv',  style={
                           'display': 'none'}, href='', download='ej-raw-data.csv', target="_blank")
                ]),
            ]),
        ])

    def add_callbacks(self):
        @self.app.callback(
            Output(f"export_{self.id_prefix}_data", 'children'),
            [Input(f"exporting_{self.id_prefix}", 'n_clicks')]
        )
        def export_callback(exporting_click):
            if(exporting_click > 0):
                return self.link_to_download()

    def link_to_download(self):
        dataAsCSV = self.filters_component.get_data_to_export().to_csv()
        urlToDownload = "data:text/csv;charset=utf-8," + \
            urllib.parse.quote(dataAsCSV)
        self.data_link_display = 'block'
        return html.A('data.csv',  style={
            'display': self.data_link_display}, href=urlToDownload, download='ej-raw-data.csv', target="_blank")

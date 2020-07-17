import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output


class CommentsComponent():

    def __init__(self, app):
        self.app = app
        self.df = None
        self.order_options = ['comentário_id',
                              'concorda', 'discorda', 'pulados']
        self.prepare()
        self.callbacks()

    def prepare(self):
        comments_df = pd.read_json('/tmp/airflow/comments_only.json')
        self.df = pd.DataFrame(data=comments_df, columns=[
            'comentário_id', 'comentário', 'autor', 'concorda', 'discorda', 'pulados', 'participação', 'convergência'])
        self.df['concorda'] = self.df['concorda'].map(
            lambda x: x * 100)
        self.df['discorda'] = self.df['discorda'].map(
            lambda x: x * 100)
        self.df['pulados'] = self.df['pulados'].map(lambda x: x * 100)
        self.df['convergência'] = self.df['convergência'].map(
            lambda x: round(x * 100))
        self.df['geral'] = ''
        for index, value in enumerate(self.df['concorda']):
            self.df['geral'][index] = [self.df['concorda'][index],
                                       self.df['discorda'][index], self.df['pulados'][index]]

    def generate_table(self):
        ths = []
        for col in self.df.columns:
            if((col != 'concorda') and (col != 'discorda') and (col != 'pulados') and (col != 'participação')):
                ths.append(html.Th(col))
        return html.Table([
            html.Thead(
                html.Tr(ths)
            ),
            html.Tbody(
                self.generate_table_body(), id="table_body"
            )
        ])

    def generate_table_body(self, new_df={}):
        df = None
        try:
            new_df.info()
            df = new_df
        except:
            df = self.df
        trs = []
        for index in range(len(df)):
            tds = []
            for col in df.columns:
                if(col == "convergência"):
                    tds.append(
                        html.Td(str(df.iloc[index][col]) + '%'))
                if(col == "geral"):
                    bar = html.Div(
                        style={},
                        children=[
                            html.Div(style={'borderStyle': 'solid', 'borderColor': 'grey', 'width': '100px', 'height': 20, 'display': 'flex'}, children=[
                                html.Div(style={
                                    'backgroundColor': 'green', 'width': df.iloc[index]['concorda'], 'height': 20}),
                                html.Div(style={
                                    'backgroundColor': 'red', 'width': df.iloc[index]['discorda'], 'height': 20}),
                                html.Div(style={
                                    'backgroundColor': 'yellow', 'width': df.iloc[index]['pulados'], 'height': 20})
                            ]),
                            html.Div(style={}, children=[
                                html.Span(style={'color': 'green', 'fontSize': '11px', 'marginRight': '5px'}, children=str(
                                    round(df.iloc[index]['concorda'])) + '%'),
                                html.Span(style={'color': 'red', 'fontSize': '11px', 'marginRight': '5px'}, children=str(
                                    round(df.iloc[index]['discorda'])) + '%'),
                                html.Span(style={'color': 'yellow', 'fontSize': '11px', 'marginRight': '5px'}, children=str(
                                    round(df.iloc[index]['pulados'])) + '%'),
                            ]),
                        ],
                    )
                    tds.append(html.Td(bar))
                elif((col != "concorda") and (col != "discorda") and (col != "pulados") and (col != 'participação') and (col != 'convergência')):
                    tds.append(html.Td(df.iloc[index][col]))
            trs.append(html.Tr(tds))
        return trs

    def _get_table(self):
        return html.Div(
            children=[
                html.Div(style={"display": "flex", "width": "20%"}, children=[
                    html.Span(style={"marginRight": 8},
                              children="Participação acima de:"),
                    dcc.Input(
                        id='participation',
                        value='50',
                        style={"flexGrow": 1}
                    ),
                ]),
                html.Div(style={"display": "flex", "width": "30%"}, children=[
                    html.Span(style={"marginRight": 8},
                              children="Ordenar por:"),
                    dcc.Dropdown(
                        id='_filter',
                        options=[{'label': i, 'value': i}
                                 for i in self.order_options],
                        value='Fertility rate, total (births per woman)',
                        style={"flexGrow": 1}
                    ),
                ]),
                self.generate_table()
            ])

    def render(self):
        return html.Div(style={'background-color': 'white', 'marginTop': '15px'},
                        children=[
            html.Div(style={"textAlign": "center", "backgroundColor": "#042a46", "color": "white", "height": "40px"},
                     children=[
                         html.Div(style={"position": "relative", "top": "20%"},
                                  children=['Votos e participação em todos os comentários, excluíndo os comentários que foram rejeitados para moderação.'])
            ]
            ),
            html.Div(style={'width': '90%', 'margin': '20px auto'}, children=[
                self._get_table()
            ])
        ])

    def callbacks(self):
        @self.app.callback(
            Output("table_body", 'children'),
            [Input('_filter', 'value'), Input('participation', 'value')])
        def table_callback(_filter, participation):
            df = self.df
            if(participation):
                df = df[df['participação'] >= int(participation) / 100]
            if(_filter in self.order_options):
                df = df.sort_values(by=_filter, ascending=False)
                return self.generate_table_body(df)
            return self.generate_table_body(df)

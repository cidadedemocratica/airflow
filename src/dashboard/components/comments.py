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
        try:
            comments_df = pd.read_json('/tmp/comments_only.json')
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
        except:
            pass

    def generate_table(self):
        ths = []
        for col in self.df.columns:
            if((col != 'concorda') and (col != 'discorda') and (col != 'pulados') and (col != 'participação')):
                ths.append(html.Th(col))
        return html.Table(style={"marginTop": 20}, children=[
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
                    tds.append(
                        html.Td(children=[df.iloc[index][col]]))
            trs.append(html.Tr(tds))
        return trs

    def _get_table(self):
        return html.Div(
            children=[
                html.Div(style={'display': 'flex', 'marginTop': '10px', 'alignItems': 'center', 'width': '30%'}, children=[
                    html.Span(style={"marginRight": 8, "fontWeight": "bold"},
                              children="Participação acima de:"),
                    dcc.Input(
                        id='participation',
                        value='50',
                        style={"flexGrow": 1}
                    ),
                ]),
                html.Div(style={'display': 'flex', 'marginTop': '10px', 'alignItems': 'center', 'width': '30%'}, children=[
                    html.Span(style={"marginRight": 8, "fontWeight": "bold"},
                              children="Ordenar por:"),
                    dcc.Dropdown(
                        id='_filter',
                        options=[{'label': i, 'value': i}
                                 for i in self.order_options],
                        value='',
                        style={"flexGrow": 1}
                    ),
                ]),
                self.generate_table()
            ])

    def render(self):
        if(self.df):
            return html.Div(className="row", children=[
                html.Div(className="col-12 mb-4", children=[
                    html.Div(className="card shadow", children=[
                        html.Div(className="card-header", children=[
                            'Votos e participação em todos os comentários.']),
                        html.Div(className="card-body", children=[
                            html.Div(children=[
                                self._get_table()
                            ])
                        ])
                    ])
                ])
            ])
        return html.Div(className="row", children=[
            html.Div(className="col-12 mb-4", children=[
                html.Div(className="card shadow", children=[
                    html.Div(className="card-header", children=[
                        'Votos e participação em todos os comentários.']),
                    html.Div(className="card-body",
                             children=["Não há dados para apresentar"])
                ])
            ])
        ])

    def callbacks(self):
        if(self.df):
            @ self.app.callback(
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

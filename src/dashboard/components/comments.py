import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

from services.comments import CommentsService


class CommentsComponent():

    def __init__(self, app):
        self.app = app
        self.service = CommentsService()
        self.df = self.service.df
        self.clusters = self.service.clusters
        self.order_options = ['comentário_id',
                              'concorda', 'discorda', 'pulados', 'convergência']
        self.prepare()

    def prepare(self):
        try:
            self.callbacks()
        except:
            pass

    def callbacks(self):
        if(not self.df.empty):
            @ self.app.callback(
                Output("table_body", 'children'),
                [Input('_filter', 'value'), Input('participation', 'value')])
            def table_callback(_filter, participation):
                df = self.df
                if(participation):
                    df = df[df['participação'] >= int(participation) / 100]
                if(_filter in self.order_options):
                    df = df.sort_values(by=_filter, ascending=False)
                    return self._generate_table_body(df)
                return self._generate_table_body(df)

    def render(self):
        if(not self.df.empty):
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

    def _generate_table(self):
        ths = []
        for col in self.df.columns:
            if((col != 'concorda') and (col != 'discorda') and (col != 'pulados') and (col != 'participação')):
                ths.append(html.Th(col))
        return html.Table(className="comments-table", children=[
            html.Thead(
                html.Tr(ths)
            ),
            html.Tbody(
                self._generate_table_body(), id="table_body"
            )
        ])

    def _generate_table_body(self, df=pd.DataFrame({})):
        if(df.empty):
            df = self.df
        trs = []
        for index in range(len(df)):
            tds = []
            for col in df.columns:
                if(col == "convergência"):
                    tds.append(
                        html.Td(str(df.iloc[index][col]) + '%'))
                cluster_columns = self._generate_clusters_columns(
                    col, df, index)
                if(cluster_columns):
                    tds.append(html.Td(cluster_columns))
                comments_columns = self._generate_comments_columns(
                    col, df, index)
                if(comments_columns):
                    tds.append(html.Td(comments_columns))
                    
                elif(col in ["autor", "comentário", "comentário_id"]):
                    tds.append(
                        html.Td(children=[df.iloc[index][col]]))
            trs.append(html.Tr(tds))
        return trs

    def _generate_comments_columns(self, col, df, index):
        if(col == "geral"):
            dom_element = html.Div(
                style={},
                children=[
                    html.Div(className='comment-bar', children=[
                        html.Div(style={
                            'backgroundColor': '#16ab39', 'width': df.iloc[index]['concorda'], 'height': 20}),
                        html.Div(style={
                            'backgroundColor': '#de011e', 'width': df.iloc[index]['discorda'], 'height': 20}),
                        html.Div(style={
                            'backgroundColor': '#042a46', 'width': df.iloc[index]['pulados'], 'height': 20})
                    ]),
                    html.Div(style={}, children=[
                        html.Span(style={'color': '#16ab39', 'fontSize': '11px', 'marginRight': '5px'}, children=str(
                            round(df.iloc[index]['concorda'])) + '%'),
                        html.Span(style={'color': '#de011e', 'fontSize': '11px', 'marginRight': '5px'}, children=str(
                            round(df.iloc[index]['discorda'])) + '%'),
                        html.Span(style={'color': '#042a46', 'fontSize': '11px', 'marginRight': '5px'}, children=str(
                            round(df.iloc[index]['pulados'])) + '%'),
                    ]),
                    html.Div(className='comment-bar', children=[
                        html.Div(style={
                            'backgroundColor': '#16ab39', 'width': df.iloc[index]['concorda'] + df.iloc[index]['discorda'], 'height': 20}),
                        html.Div(style={
                            'backgroundColor': '#042a46', 'width': df.iloc[index]['pulados'], 'height': 20}),
                    ]),
                    html.Div(style={}, children=[
                        html.Span(style={'color': '#16ab39', 'fontSize': '11px', 'marginRight': '5ax'}, children=str(
                            round(df.iloc[index]['concorda'] + df.iloc[index]['discorda'])) + '%'),
                        html.Span(style={'color': '042a46', 'fontSize': '11px', 'marginRight': '5ax'}, children=str(
                            round(df.iloc[index]['pulados'])) + '%'),
                    ]),
                ],
            )
            return dom_element
        else:
            return None
    
    def _generate_clusters_columns(self, col, df, index):
        if(col in CommentsService._get_clusters_name(self)):
            cluster_votes_statistics = df.iloc[index][col].split(',')
            bar = html.Div(
                style={},
                children=[
                    html.Div(className='comment-bar', children=[
                        html.Div(style={
                            'backgroundColor': '#16ab39', 'width': round(float(cluster_votes_statistics[0])), 'height': 20}),
                        html.Div(style={
                            'backgroundColor': '#de011e', 'width': round(float(cluster_votes_statistics[1])), 'height': 20}),
                        html.Div(style={
                            'backgroundColor': '#042a46', 'width': round(float(cluster_votes_statistics[2])), 'height': 20})
                    ]),
                    html.Div(style={}, children=[
                        html.Span(style={'color': '#16ab39', 'fontSize': '11px', 'marginRight': '5px'}, children=str(
                            round(float(cluster_votes_statistics[0]))) + '%'),
                        html.Span(style={'color': '#de011e', 'fontSize': '11px', 'marginRight': '5px'}, children=str(
                            round(float(cluster_votes_statistics[1]))) + '%'),
                        html.Span(style={'color': '#042a46', 'fontSize': '11px', 'marginRight': '5px'}, children=str(
                            round(float(cluster_votes_statistics[2]))) + '%'),
                    ]),
                    html.Div(className='comment-bar', children=[
                        html.Div(style={
                            'backgroundColor': '#16ab39', 'width': round(float(cluster_votes_statistics[0]) + 
                                float(cluster_votes_statistics[1])), 'height': 20}),
                        html.Div(style={
                            'backgroundColor': '#042a46', 'width': round(float(cluster_votes_statistics[2])), 'height': 20}),
                    ]),
                    html.Div(style={}, children=[
                        html.Span(style={'color': '#16ab39', 'fontSize': '11px', 'marginRight': '5ax'}, children=str(
                            round(float(cluster_votes_statistics[0]) + float(cluster_votes_statistics[1]))) + '%'),
                        html.Span(style={'color': '042a46', 'fontSize': '11px', 'marginRight': '5ax'}, children=str(
                            round(float(cluster_votes_statistics[2]))) + '%'),
                    ]),

                ],
            )
            return bar
        return None

    def _get_table(self):
        return html.Div(
            children=[
                html.Div(style={'display': 'flex', 'marginTop': '10px', 'alignItems': 'center', 'width': '30%'}, children=[
                    html.Span(style={"marginRight": 8, "fontWeight": "bold"},
                              children="ID da Conversa: 45"),
                ]),
                html.Div(style={'display': 'flex', 'marginTop': '10px', 'alignItems': 'center', 'width': '30%'}, children=[
                    html.Span(style={"marginRight": 8, "fontWeight": "bold"},
                              children="Participação acima de:"),
                    dcc.Input(
                        id='participation',
                        value='50',
                        style={"flexGrow": 1}
                    ),
                ]),
                html.Div(style={'display': 'flex', 'marginTop': '10px', 'margin-bottom' : '18px', 'alignItems': 'center', 'width': '30%'}, children=[
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
                html.Div(style={'maxWidth': '100vw', 'overflow': 'scroll', 'maxHeight': '600px'},  children=[
                         self._generate_table()])
            ])


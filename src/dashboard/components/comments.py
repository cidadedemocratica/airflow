import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

from services.comments import CommentsService
from components.utils.export import ExportsComponent


class CommentsComponent():

    def __init__(self, app):
        self.app = app
        self.service = CommentsService()
        self.export_component = ExportsComponent("comments")
        self.comments = self.service.comments
        self.clusters = self.service.clusters
        self.order_options = ['concorda',
                              'discorda', 'pulados', 'convergência']
        self.add_callbacks()

    def add_callbacks(self):
        if(not self.comments.empty):
            @self.app.callback(
                Output("comments_download_export", 'href'),
                [Input("comments_exports_df", 'n_clicks')]
            )
            def export_callback(export_df):
                return self.export_component.export(self.comments)

            @self.app.callback(
                Output("table_body", 'children'),
                [Input('_filter', 'value'), Input('participation', 'value')])
            def table_callback(_filter, participation):
                df = self.comments
                if(participation):
                    df = df[df['participação'] >= int(participation) / 100]
                if(_filter in self.order_options):
                    df = df.sort_values(by=_filter, ascending=False)
                    return self._generate_table_body(df)
                return self._generate_table_body(df)

    def render(self):
        if(not self.comments.empty):
            return html.Div(className="row", children=[
                html.Div(className="col-12 mb-4", children=[
                    html.Div(className="card shadow", children=[
                        html.Div(className="card-header", children=[
                            'Votos e participação em todos os comentários.']),
                        html.Div(className="card-body", children=[
                            html.Div(children=[
                                dcc.Loading(id="comments_loader", type="default", color="#30bfd3", children=[
                                    html.Div(id="commments_filters",
                                             children=[self._get_table()])
                                ]),
                                html.Hr(),
                                self.export_component.render(),
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
        for col in self.comments.columns:
            if(col in ["comentário_id", "comentário", "autor", "convergência"]):
                ths.append(html.Th(col))
        ths.append(html.Th("clusters"))
        return html.Table(className="comments-table", children=[
            html.Thead(
                html.Tr(ths)
            ),
            html.Tbody(
                self._generate_table_body(), id="table_body",
            ),
        ])

    def _generate_table_body(self, df=pd.DataFrame({})):
        if(df.empty):
            df = self.comments
        trs = []
        for index in range(len(df)):
            tds = []
            tds_clusters = []
            for col in df.columns:
                if(col == "convergência"):
                    tds.append(
                        html.Td(str(round(df.iloc[index][col] * 100)) + '%'))
                geral_bar = self._get_geral_bar(
                    col, df, index)
                cluster_bars = self._get_clusters_bars(
                    col, df, index)
                if(geral_bar):
                    tds_clusters.append(geral_bar)
                if(cluster_bars):
                    tds_clusters.append(cluster_bars)
                elif(col in ["autor", "comentário"]):
                    tds.append(
                        html.Td(children=[df.iloc[index][col]]))
            tds.append(html.Td(className='clusters', children=tds_clusters))
            trs.append(html.Tr(tds))
        return trs

    def _get_geral_bar(self, col, df, index):
        if(col == "geral"):
            dom_element = html.Div(
                children=[
                    html.Div(className='clusters-name', children=[
                        html.Span(col)
                    ]),
                    html.Div(className='comment-bar', children=[
                        html.Div(style={
                            'backgroundColor': '#16ab39', 'width': df.iloc[index]['concorda'] * 100, 'height': 20}),
                        html.Div(style={
                            'backgroundColor': '#de011e', 'width': df.iloc[index]['discorda'] * 100, 'height': 20}),
                        html.Div(style={
                            'backgroundColor': '#042a46', 'width': df.iloc[index]['pulados'] * 100, 'height': 20})
                    ]),
                    html.Div(style={}, children=[
                        html.Span(className="agree", children=str(
                            round(df.iloc[index]['concorda'] * 100)) + '%'),
                        html.Span(className="disagree", children=str(
                            round(df.iloc[index]['discorda'] * 100)) + '%'),
                        html.Span(className="skipped", children=str(
                            round(df.iloc[index]['pulados'] * 100)) + '%'),
                    ]),
                    self._get_participation_bar(
                        df.iloc[index]['participação'] * 100)
                ],
            )
            return dom_element
        else:
            return None

    def _get_participation_bar(self, value):
        return html.Div(children=[
            html.Div(className='clusters-name', children=[
                html.Span("participação")
            ]),
            html.Div(className='comment-bar', children=[
                html.Div(style={
                    'backgroundColor': '#30bfd3', 'width': value, 'height': 20,
                    'opacity': '90%'}),
                html.Div(style={
                    'backgroundColor': '#858796', 'width': 100 - value, 'height': 20, 'opacity': '56%'}),
            ]),
            html.Div(style={}, children=[
                html.Span(className="participation", children=str(
                    round(value)) + '%'),
                html.Span(className="no-participation", children=str(
                    round(100 - value)) + '%')
            ]),
        ])

    def _get_clusters_bars(self, col, df, index):
        if(col in CommentsService.get_clusters_name(self)):
            cluster_votes_statistics = df.iloc[index][col].split(',')
            cluster_votes_participation = df.iloc[index][f"{col}_participation"]
            bar = html.Div(
                style={},
                children=[
                    html.Div(className='clusters-name', children=[
                        html.Span(col)
                    ]),
                    html.Div(className='comment-bar', children=[
                        html.Div(style={
                            'backgroundColor': '#16ab39', 'width': round(float(cluster_votes_statistics[0])), 'height': 20}),
                        html.Div(style={
                            'backgroundColor': '#de011e', 'width': round(float(cluster_votes_statistics[1])), 'height': 20}),
                        html.Div(style={
                            'backgroundColor': '#042a46', 'width': round(float(cluster_votes_statistics[2])), 'height': 20})
                    ]),
                    html.Div(style={}, children=[
                        html.Span(className="agree", children=str(
                            round(float(cluster_votes_statistics[0]))) + '%'),
                        html.Span(className="disagree", children=str(
                            round(float(cluster_votes_statistics[1]))) + '%'),
                        html.Span(className="skipped", children=str(
                            round(float(cluster_votes_statistics[2]))) + '%'),
                    ]),
                    self._get_participation_bar(
                        float(cluster_votes_participation))
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
                        type='number',
                        value='50',
                        style={"flexGrow": 1, 'color': '#aaa', 'padding': '6px', 'opacity': '60%'}),
                ]),
                html.Div(style={'display': 'flex', 'marginTop': '10px', 'marginBottom': '18px', 'alignItems': 'center', 'width': '30%'}, children=[
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
                html.Div(className='table-wrapper',
                         children=[self._generate_table()])
            ])

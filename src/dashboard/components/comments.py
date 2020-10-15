import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from services.comments import CommentsService
from components.utils.export import ExportsComponent


class CommentsComponent():

    def __init__(self, app):
        self.app = app
        self.service = CommentsService()
        self.comments = self.service.comments
        self.order_options = ['concorda',
                              'discorda', 'pulados', 'convergência']
        self.export_component = ExportsComponent(
            "comments", app, self.comments)
        self.add_callbacks()

    def add_callbacks(self):
        @self.app.callback(
            Output("table_body", 'children'),
            [Input('_filter', 'value'),
             Input('app_reload', 'n_clicks'),
             Input('participation', 'value')])
        def table_callback(_filter, app_reload, participation):
            if(app_reload != 0):
                self.service.load_data()
                self.comments = self.service.comments
            if(self.comments.empty):
                return self._generate_table_body()
            df = self.comments
            if(participation):
                df = df[df['participação'] >= int(participation) / 100]
            if(_filter in self.order_options):
                df = df.sort_values(by=_filter, ascending=False)
                return self._generate_table_body(df)
            self.export_component.df = df
            return self._generate_table_body(df)

    def render(self):
        if(not self.comments.empty):
            return html.Div(className="row", children=[
                html.Div(className="col-12 mb-4", children=[
                    html.Div(className="card shadow", children=[
                        html.Div(className="card-header", children=[
                            'Votos e participação em todos os comentários.'
                        ]),
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
                    html.Div(className="card-body", children=[
                        html.Div(children=[
                            html.Span("Não há dados para apresentar"),
                            dcc.Loading(id="comments_loader", type="default", color="#30bfd3", children=[
                                html.Div(id="commments_filters",
                                         children=[self._get_table()])
                            ]),
                        ])
                    ])
                ])
            ])
        ])

    def _generate_table(self):
        ths = []
        for col in self.comments.columns:
            if(col in ["comentário", "convergência"]):
                ths.append(html.Th(col))
        clusters = [
            html.Div("clusters", className='cluster-info'),
            html.Div(className="fa fa-info-circle", id='clusters-hover'),                     
            dbc.Tooltip(
                'Barra Superior: Percentual de votantes que concordaram, '\
                    'discordaram ou pularam o comentário.'\
                    '\nBarra Inferior: Percentual de participação no'\
                    'comentário considerando todos os participantes da '\
                    'conversa ou do cluster.',
                target="clusters-hover",
                placement="bottom",
                className="hover-comments-bar"
            )]
        ths.append(html.Th(clusters))
        return html.Table(className="comments-table", children=[
            html.Div(className='table-wrapper', children=[
                html.Thead(
                    html.Tr(ths)
                ),
                html.Tbody(
                    self._generate_table_body(), id="table_body",
                ),
            ])
        ])

    def _generate_table_body(self, df=pd.DataFrame({})):
        if(self.comments.empty):
            return
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
                elif(col == "comentário"):
                    tds.append(
                        html.Td(children=[
                            html.Div(children=[df.iloc[index][col]]),
                            html.Div(className="comments-infos", children=["id: " + 
                            str(df.iloc[index]['comentário_id']), html.Br(),
                            "autor: " + str(df.iloc[index]['autor'])])
                            ]))
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
        if(col in self.service.get_clusters_names()):
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
                              children="ID da Conversa: 56"),
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
                html.Div(children=[self._generate_table()])
            ])

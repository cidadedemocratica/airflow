import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from components.comments.filters import FiltersComponent
from components.utils.export import ExportsComponent


class CommentsComponent():

    def __init__(self, app):
        self.app = app
        self.filters_component = FiltersComponent(app, self._generate_table)
        self.comments = self.filters_component.comments
        self.clusters = self.filters_component.clusters
        self.conversation_url = "https://www.ejplatform.org/conversations/56/ucc-conversa-1/"
        self.export_component = ExportsComponent(
            "comments", app, self.filters_component)

    def render(self):
            return html.Div(className="row", children=[
                html.Div(className="col-12 mb-4", children=[
                    html.Div(className="card shadow", children=[
                        html.Div(className="card-header", children=[
                            html.Div(children=[
                                html.Span('Votos e participação em todos os comentários.', style={
                                    "marginRight": 4}),
                                html.I(className="fa fa-info-circle",
                                       id='comments-component-title')
                            ]),
                            dbc.Tooltip(
                                'Visualização que permite correlacionar como cada comentário performou no geral e nos clusters.',
                                target='comments-component-title')

                        ]),
                        html.Div(className="card-body", children=[
                            html.Div(children=[
                                dcc.Loading(id="comments_loader", type="default", color="#30bfd3", children=[
                                    html.Div(id="commments_filters",
                                             children=[self._get_table()])
                                ]),
                                html.Hr(),
                            ])
                        ])
                    ])
                ])
            ])

    def _generate_table(self, comments):
        if (comments.empty):
            return html.Div(className="row", children=[
                html.Div(className="col-12 mb-4", children=[
                    html.Div(className="card shadow", children=[
                        html.Div(className="card-header", children=[
                            'Votos e participação em todos os comentários.']),
                        html.Div(className="card-body", children=[
                            html.Div(children=[
                                html.Span("Não há dados para apresentar"),
                            ])
                        ])
                    ])
                ])
            ])
        ths = []
        for col in self.comments.columns:
            if(col in ["comentário", "convergência"]):
                ths.append(html.Th(col))
        clusters = [
            html.Div("clusters", className='cluster-info'),
            html.Div(className="fa fa-info-circle", id='clusters-hover'),
            dbc.Tooltip(
                'Barra Superior: Percentual de votantes que concordaram, '
                'discordaram ou pularam o comentário.'
                '\nBarra Inferior: Percentual de participação no'
                'comentário considerando todos os participantes da '
                'conversa ou do cluster.',
                target="clusters-hover",
                placement="bottom",
                className="hover-comments-bar"
            )]
        ths.append(html.Th(clusters))
        return html.Table(className="comments-table", id="table_body", children=[
            html.Thead(
                html.Tr(ths)
            ),
            html.Tbody(
                self._generate_table_body(comments, self.clusters)
            ),
        ])

    def _generate_table_body(self, comments, clusters): 
        trs = []
        for index in range(len(comments)):
            tds = []
            tds_clusters = []
            for col in comments.columns:
                if(col == "convergência"):
                    tds.append(
                        html.Td(str(round(comments.iloc[index][col] * 100)) + '%'))
                geral_bar = self._get_geral_bar(
                    col, comments, index)
                cluster_bars = self._get_clusters_bars(
                    col, comments, clusters, index)
                if(geral_bar):
                    tds_clusters.append(geral_bar)
                if(cluster_bars):
                    tds_clusters.append(cluster_bars)
                elif(col == "comentário"):
                    tds.append(
                        html.Td(children=[
                            html.Div(children=[comments.iloc[index][col]]),
                            html.Div(className="comments-infos", children=[
                                "id: " + str(comments.iloc[index]['comentário_id']),
                                html.Br(),
                                "autor: " + str(comments.iloc[index]['autor'])])
                        ]))
            tds.append(html.Td(className='clusters', children=tds_clusters))
            trs.append(html.Tr(tds))
        return trs

    def _get_geral_bar(self, col, comments, index):
        if(col == "geral"):
            dom_element = html.Div(
                children=[
                    html.Div(className='clusters-name', children=[
                        html.Span(col)
                    ]),
                    html.Div(className='comment-bar', children=[
                        html.Div(style={
                            'backgroundColor': '#16ab39', 'width': comments.iloc[index]['concorda'] * 100, 'height': 20}),
                        html.Div(style={
                            'backgroundColor': '#de011e', 'width': comments.iloc[index]['discorda'] * 100, 'height': 20}),
                        html.Div(style={
                            'backgroundColor': '#042a46', 'width': comments.iloc[index]['pulados'] * 100, 'height': 20})
                    ]),
                    html.Div(style={}, children=[
                        html.Span(className="agree", children=str(
                            round(comments.iloc[index]['concorda'] * 100)) + '%'),
                        html.Span(className="disagree", children=str(
                            round(comments.iloc[index]['discorda'] * 100)) + '%'),
                        html.Span(className="skipped", children=str(
                            round(comments.iloc[index]['pulados'] * 100)) + '%'),
                    ]),
                    self._get_participation_bar(
                        comments.iloc[index]['participação'] * 100)
                ],
            )
            return dom_element
        else:
            return None

    def _get_participation_bar(self, value):
        return html.Div(children=[
            html.Div(className='comment-bar', children=[
                html.Div(style={
                    'backgroundColor': '#30bfd3', 'width': value, 'height': 20}),
                html.Div(style={
                    'backgroundColor': '#c9cbd1', 'width': 100 - value, 'height': 20}),
            ]),
            html.Div(style={}, children=[
                html.Span(className="participation", children=str(
                    round(value)) + '%'),
                html.Span(className="no-participation", children=str(
                    round(100 - value)) + '%')
            ]),
        ])

    def get_clusters_names(self, clusters):
        clusters_names = clusters.cluster_name.value_counts().keys()
        clusters_names = clusters_names.map(
            lambda cluster_name: f"{cluster_name}")
        return clusters_names

    def _get_clusters_bars(self, col, comments, clusters, index):
        if(col in self.get_clusters_names(clusters)):
            cluster_votes_statistics = comments.iloc[index][col].split(',')
            cluster_votes_participation = comments.iloc[index][f"{col}_participation"]
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
        return html.Div(children=[
                html.Div(style={'display': 'flex', 'marginTop': '10px', 
                                'alignItems': 'center', "fontWeight": "bold"},
                    children=[
                        html.Span(className="filter-title",
                            children=[html.Span("Conversa: "),
                                html.A(self.conversation_url,
                                    href=self.conversation_url,
                                        target="_blank")
                            ]),
                ]),
                html.Div(children=[
                    self.filters_component.render(),
                    self.export_component.render()
                 ]),
                html.Div(className='table-wrapper',
                    children=[self._generate_table(self.comments)])
            ])

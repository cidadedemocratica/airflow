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

CONVERSATION_URL = "https://www.ejplatform.org/conversations/56/ucc-conversa-1/"


class CommentsComponent():

    def __init__(self, app):
        self.app = app
        self.filters_component = FiltersComponent(app, self._get_table)
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
                                html.Div(children=[self._get_body()])
                            ]),
                            html.Hr(),
                        ])
                    ])
                ])
            ])
        ])

    def _get_body(self):
        return html.Div(children=[
            html.Div(className='comments-conversation-link',
                     children=[
                        html.Span(className="filter-title",
                                  children=[html.Span("Conversa: "),
                                            html.A(CONVERSATION_URL,
                                                   href=CONVERSATION_URL,
                                                   target="_blank")
                                            ]),
                        ]),
            html.Div(children=[self.filters_component.render(),
                               self.export_component.render()]),
            html.Div(className='table-wrapper', children=[self._get_table()])
        ])

    def _get_table(self, comments=pd.DataFrame({}), clusters=pd.DataFrame({})):
        if (comments.empty):
            return self._empty_table()
        return html.Table(className="comments-table", id="table_body", children=[
            html.Thead(html.Tr(self._get_table_columns(comments))),
            html.Tbody(self._get_table_body(comments, clusters)),
        ])

    def _get_table_columns(self, comments):
        ths = []
        for col in comments.columns:
            if(col in ["comentário", "convergência"]):
                ths.append(html.Th(col))
        clusters_th = [
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
        ths.append(html.Th(clusters_th))
        return ths

    def _empty_table(self):
        return html.Div(className="card-body", children=[
                        html.Div(id="table_body", children=[
                                 html.Span("Não há dados para apresentar"), ])
                        ])

    def _get_table_body(self, comments, clusters):
        trs = []
        for comment in comments.iterrows():
            tds = []
            row = comment[1]
            tds.append(self._get_comentario_row(row))
            tds.append(self._get_convergencia_row(row))
            tds.append(self._get_clusters_row(row, clusters))
            trs.append(html.Tr(tds))

        return trs

    def _get_comentario_row(self, comment):
        return html.Td(children=[
            html.Div(children=[comment['comentário']]),
            html.Div(className="comments-infos", children=[
                "id: " +
                str(comment['comentário_id']),
                html.Br(),
                "autor: " + str(comment['autor'])])
        ])

    def _get_convergencia_row(self, comment):
        return html.Td(str(round(comment['convergência'] * 100)) + '%')

    def _get_clusters_row(self, comment, clusters):
        tds_clusters = []
        tds_clusters.append(self._get_geral_bar(comment))
        tds_clusters.extend(self._get_clusters_bars(comment, clusters))
        return html.Td(className='clusters', children=tds_clusters)

    def _get_geral_bar(self, comment):
        return html.Div(
            children=[
                html.Div(className='clusters-name', children=[
                    html.Span("geral")
                ]),
                html.Div(className='comment-bar', children=[
                    html.Div(style={
                        'backgroundColor': '#16ab39', 'width': comment.concorda * 100, 'height': 20}),
                    html.Div(style={
                        'backgroundColor': '#de011e', 'width': comment.discorda * 100, 'height': 20}),
                    html.Div(style={
                        'backgroundColor': '#042a46', 'width': comment.pulados * 100, 'height': 20})
                ]),
                html.Div(style={}, children=[
                    html.Span(className="agree", children=str(
                        round(comment.concorda * 100)) + '%'),
                    html.Span(className="disagree", children=str(
                        round(comment.discorda * 100)) + '%'),
                    html.Span(className="skipped", children=str(
                        round(comment.pulados * 100)) + '%'),
                ]),
                self._get_participation_bar(
                    comment['participação'] * 100)
            ],
        )

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

    def _get_clusters_bars(self, comment, clusters):
        clusters_names = clusters.cluster_name.value_counts().keys()
        tds = []
        for cluster in clusters_names:
            cluster_votes_statistics = comment[cluster].split(',')
            cluster_votes_participation = comment[f"{cluster}_participation"]
            tds.append(html.Div(
                style={},
                children=[
                    html.Div(className='clusters-name', children=[
                        html.Span(cluster)
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
            ))
        return tds

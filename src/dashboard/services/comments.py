import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output


class CommentsService():
    """
        CommnetsService represents a object controls CommentsComponent data.
    """

    def __init__(self):
        self.df = pd.DataFrame({})
        self.clusters = pd.DataFrame({})
        self.prepare()

    def prepare(self):
        """
            reads the data stored by airflow on /tmp/comments.json.
            reads the data stored by airflow on /tmp/clusters.json.
            show clusters statistics by comments
        """
        try:
            self.df = pd.read_json('/tmp/comments.json')
            self.clusters = pd.read_json('/tmp/clusters.json')
            self._format_coluns()
            self._merge_clusters_and_comments()
        except Exception as err:
            print(f"Error on comments service: {err}")

    def get_clusters_name(self):
        clusters_names = self.clusters.Grupos.value_counts().keys()
        clusters_names = clusters_names.map(
            lambda cluster_name: f"cluster_{cluster_name}")
        return clusters_names

    def _format_coluns(self):
        self.df = pd.DataFrame(data=self.df, columns=[
            'comentário_id', 'comentário', 'autor', 'concorda', 'discorda', 'pulados', 'participação', 'convergência'])
        self.df['concorda'] = self.df['concorda'].map(
            lambda x: x * 100)
        self.df['discorda'] = self.df['discorda'].map(
            lambda x: x * 100)
        self.df['pulados'] = self.df['pulados'].map(lambda x: x * 100)
        self.df['participação'] = self.df['participação'].map(
            lambda x: x * 100)
        self.df['convergência'] = self.df['convergência'].map(
            lambda x: round(x * 100))
        self.df['geral'] = ''
        for index, value in enumerate(self.df['geral']):
            self.df.loc[index,
                        'geral'] = f"{self.df.loc[index, 'concorda']}, {self.df.loc[index, 'discorda']}, {self.df.loc[index, 'pulados']}"

    def _merge_clusters_and_comments(self):
        self.clusters = self.clusters.rename(columns={
            "concorda": "cluster_concorda", "desagree": "cluster_discorda", "skip": "cluster_pulado", "comentário_id": "cluster_comentário_id"})
        for index, value in enumerate(self.df['comentário']):
            comment_clusters = self.clusters[self.clusters['comentário'] == value]
            comment_clusters.loc[comment_clusters['comentário'] == value, 'cluster_concorda'] = comment_clusters['cluster_concorda'].map(
                lambda x: x * 100)
            comment_clusters.loc[comment_clusters['comentário'] == value, 'cluster_discorda'] = comment_clusters['cluster_discorda'].map(
                lambda x: x * 100)
            comment_clusters.loc[comment_clusters['comentário'] == value, 'cluster_pulado'] = comment_clusters['cluster_pulado'].map(
                lambda x: x * 100)
            for index2, cluster_name in enumerate(comment_clusters['cluster']):
                self.df.loc[index, f'cluster_{cluster_name}'] = f"{comment_clusters.iloc[index2]['cluster_concorda']}, {comment_clusters.iloc[index2]['cluster_discorda']}, {comment_clusters.iloc[index2]['cluster_pulado']}"

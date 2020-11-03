import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import traceback


class CommentsService():
    """
        CommnetsService represents a object controls CommentsComponent data.
    """

    def __init__(self):
        self.load_data()

    def load_data(self):
        """
            reads the data stored by airflow on /tmp/comments.json.
            reads the data stored by airflow on /tmp/clusters.json.
            show clusters statistics by comments
        """
        self.comments = pd.DataFrame({})
        self.clusters = pd.DataFrame({})
        try:
            self.comments = pd.read_json('/tmp/comments.json')
            self.clusters = pd.read_json('/tmp/clusters.json')
            self._create_geral_column()
            self._create_clusters_columns()
        except Exception as err:
            print(traceback.format_exc())
            pass


    def _create_geral_column(self):
        self.comments = pd.DataFrame(data=self.comments, columns=[
            'comentário_id','comentário', 'autor', 'concorda', 'discorda', 'pulados', 
            'participação', 'convergência'])
        self.comments['geral'] = ''
        for index, value in enumerate(self.comments['geral']):
            self.comments.loc[index,
                              'geral'] = f"{self.comments.loc[index, 'concorda']}, {self.comments.loc[index, 'discorda']}, {self.comments.loc[index, 'pulados']}"

    def _create_clusters_columns(self):
        for index, comment in enumerate(self.comments['comentário']):
            comment_clusters = self.clusters[self.clusters['conteúdo'] == comment]
            for index2, cluster_name in enumerate(comment_clusters.cluster_name):
                self.comments.loc[index, f'{cluster_name}'] = f"{comment_clusters.iloc[index2]['concorda']}, {comment_clusters.iloc[index2]['discorda']}, {comment_clusters.iloc[index2]['pulados']}"
                self.comments.loc[index,
                                  f'{cluster_name}_participation'] = f"{comment_clusters.iloc[index2]['participação']}"

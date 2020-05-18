import os
import json
import datetime
import pandas as pd
import time
from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
from dateutil.parser import *
from airflow.utils.dates import days_ago

from src.operators import votes_compiler
from src.operators import comments_compiler
from src import analytics_api as analytics


class EjOperator(BaseOperator):

    @apply_defaults
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        analytics_client = analytics.initialize_analyticsreporting()
        self.votes_compiler = votes_compiler.VotesCompiler(analytics_client)
        self.comments_compiler = comments_compiler.CommentsCompiler(
            analytics_client)

    def execute(self, context):
        ej_votes = self.get_ej_votes_from_xcom(context)
        mautic_contacts = self.get_mautic_contacts_from_xcom(context)
        ej_comments = self.get_ej_comments_from_xcom(context)
        compiled_votes = self.votes_compiler.compile(ej_votes, mautic_contacts)
        compiled_comments = self.comments_compiler.compile(
            ej_comments, mautic_contacts)

        self.votes_compiler.merge_with_analytics(compiled_votes)
        self.comments_compiler.merge_with_analytics(compiled_comments)
        return 'DataFrame with EJ, Mautic and Analytics data, generated on /tmp/ej_analytics_mautic.csv'

    def get_ej_votes_from_xcom(self, context):
        return json.loads(context['task_instance'].xcom_pull(
            task_ids='request_ej_votes'))

    def get_ej_comments_from_xcom(self, context):
        return json.loads(context['task_instance'].xcom_pull(
            task_ids='request_ej_comments'))

    def get_mautic_contacts_from_xcom(self, context):
        return json.loads(context['task_instance'].xcom_pull(
            task_ids='request_mautic_contacts'))["contacts"]

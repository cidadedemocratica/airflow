import os
import json
import datetime
import pandas as pd
import time
import json
import requests

from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.hooks.base_hook import BaseHook
from src.airflow.operators import helper


class MauticApiOperator(BaseOperator):

    @apply_defaults
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.helper = helper.OperatorHelper()
        self.connection = BaseHook.get_connection("mautic_prod_api")
        self.df = None
        self.votes_df = None

    def execute(self, context):
        self._get_votes()
        df = self.merge_votes_and_contacts()
        self._df_to_json(df)

    def _get_votes(self):
        self.votes_df = pd.read_json('/tmp/votes_analytics.json')

    def merge_votes_and_contacts(self):
        votes = pd.DataFrame(self.votes_df)
        votes['mtc_email'] = ''
        votes['mtc_first_name'] = ''
        votes['mtc_last_name'] = ''
        uniq_emails = votes.groupby(
            'email').count().reset_index(level=0)
        print(
            f'Airflow will request {len(uniq_emails)} contacts on mautic api')
        for counter, row in enumerate(uniq_emails.loc()):
            try:
                mtc_id = str(int(row["author__metadata__mautic_id"]))
                if(mtc_id):
                    mtc_contact = self._get_contact(mtc_id)
                    votes = self.helper.merge(
                        votes, mtc_contact, row["email"])
                    votes.to_json('/tmp/votes_analytics_mautic.json')
                print(f'{counter} requests made. Contact {row["email"]}')
                if(counter == len(uniq_emails) - 1):
                    break
            except:
                pass
        return votes

    def _get_contact(self, mtc_id):
        url = self._get_url(mtc_id)
        headers = {
            "Authorization": f'Basic cmljYXJkb0BjaWRhZGVkZW1vY3JhdGljYS5vcmcuYnI6cVlVNjQzNHJPRjNQ'}
        response = requests.get(url, headers=headers)
        return response.json()['contact']

    def _get_url(self, mtc_id):
        return f"{self.connection.schema}://{self.connection.host}/api/contacts/{mtc_id}"

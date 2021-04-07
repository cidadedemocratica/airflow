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
from operators import helper


class MauticApiOperator(BaseOperator):

    @apply_defaults
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.helper = helper.OperatorHelper()
        self.connection = BaseHook.get_connection("mautic_dev_api")
        self.df = None
        self.votes_df = None

    def execute(self, context):
        self._get_votes()
        self.merge_votes_and_contacts()

    def _get_votes(self):
        self.votes_df = pd.read_json('/tmp/votes.json')

    def merge_votes_and_contacts(self):
        votes = pd.DataFrame(self.votes_df)
        votes['mtc_email'] = ''
        votes['mtc_first_name'] = ''
        votes['mtc_last_name'] = ''
        mtc_ids = votes.author__metadata__mautic_id.value_counts().keys()
        print(
            f'Airflow will request {len(mtc_ids)} contacts on mautic api')
        for mtc_id in mtc_ids:
            try:
                mtc_id = str(int(mtc_id))
                if(mtc_id):
                    mtc_contact = self._get_contact(mtc_id)
                    votes = self._merge(votes, mtc_contact, mtc_id)
                    votes.to_json('/tmp/votes_mautic.json')
                print(f'mautic id {mtc_id} requested')
            except Exception as err:
                print(f'{err}')
                pass

    def _get_contact(self, mtc_id):
        url = self._get_url(mtc_id)
        headers = {
            "Authorization": f'Basic cmljYXJkb0BjaWRhZGVkZW1vY3JhdGljYS5vcmcuYnI6cVlVNjQzNHJPRjNQ'}
        response = requests.get(url, headers=headers)
        return response.json()['contact']

    def _get_url(self, mtc_id):
        return f"{self.connection.schema}://{self.connection.host}/api/contacts/{mtc_id}"

    def _merge(self, df, contact, mtc_id):
        mautic_email = contact["fields"]["all"]["email"]
        first_name = contact["fields"]["all"]["firstname"]
        last_name = contact["fields"]["all"]["lastname"]
        df.loc[df['email'] == f'{mtc_id}-mautic@mail.com',
               'mtc_email'] = mautic_email
        df.loc[df['email'] == f'{mtc_id}-mautic@mail.com',
               'mtc_first_name'] = first_name
        df.loc[df['email'] == f'{mtc_id}-mautic@mail.com',
               'mtc_last_name'] = last_name
        return df

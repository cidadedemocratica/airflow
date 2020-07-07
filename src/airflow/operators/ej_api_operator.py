import os
import json
import datetime
import pandas as pd
import time
import json
import requests

from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.utils.dates import days_ago
from airflow.hooks.base_hook import BaseHook


class EjApiOperator(BaseOperator):

    @apply_defaults
    def __init__(self, conversation_id: str, data_type: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.connection = BaseHook.get_connection("ej_prod_api")
        self.conversation_id = conversation_id
        self.data_type = data_type

    def execute(self, context):
        url = self._get_url()
        data = self._make_request(url)
        self._write(data)

    def _make_request(self, url):
        response = requests.get(url, headers={
            "Accept": "text/csv"})
        return response.json()

    def _write(self, data):
        file_name = f"{self.data_type}.json"
        with open(f'/tmp/{file_name}', 'w') as f:
            f.write(json.dumps(data))

    def _get_url(self):
        return f"{self.connection.schema}://{self.connection.host}/api/v1/conversations/{self.conversation_id}/reports?fmt=json&&export={self.data_type}"

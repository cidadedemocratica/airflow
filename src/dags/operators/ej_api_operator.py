import os
import json
import datetime
import pandas as pd
import time
import json
import requests
from typing import Dict, Optional

from airflow.models.baseoperator import BaseOperator
from airflow.hooks.base_hook import BaseHook


class EjApiOperator(BaseOperator):

    template_fields = ('conversation_id',)

    def __init__(self, conversation_id: str, data_type: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.conversation_id = conversation_id
        self.data_type = data_type

    def execute(self, context):
        self.setup()
        self.authenticate()
        votes = self.get_ej_votes()
        self.save(votes)

    def setup(self):
        self.connection = BaseHook.get_connection("ej_dev_api")
        print("conversation_id")
        print(self.conversation_id)
        print("conversation_id")
        self.ej_host_url = f"{self.connection.schema}://{self.connection.host}";
        self.ej_conversation_url = f"{self.ej_host_url}/api/v1/conversations/{self.conversation_id}/votes?startDate=2021-04-01&endDate=2021-07-01"
        self.ej_auth_url = f"{self.ej_host_url}/rest-auth/registration/"
        self.token = ""
        self.auth_body = {
            "email": "contato@pencillabs.com.br",
            "name": "Pencillabs"
        }

    def authenticate(self):
        response = self.request(self.ej_auth_url, "post", self.auth_body, {})
        self.token = response.get('key')

    def get_ej_votes(self):
        return self.request(self.ej_conversation_url,"get", {}, {'Authorization': f"Token {self.token}"})

    def request(self, url, method="get", body={}, headers={}):
        response = None
        if method == "post":
            response = requests.post(url, body, headers=headers)
        if method == "get":
            response = requests.get(url, headers=headers)
        if response.status_code == 201 or response.status_code == 200:
            return response.json()
        else:
            raise Exception("could not get user auth token")

    def save(self, data):
        file_name = f"{self.data_type}.json"
        with open(f'/tmp/{file_name}', 'w') as f:
            f.write(json.dumps(data))

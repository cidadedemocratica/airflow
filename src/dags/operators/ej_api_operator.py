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

    template_fields = (
        "conversation_id",
        "conversation_start_date",
        "conversation_end_date",
    )

    def __init__(
        self,
        conversation_id: str,
        data_type: str,
        conversation_start_date: str,
        conversation_end_date: str,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.conversation_id = conversation_id
        self.conversation_start_date = conversation_start_date
        self.conversation_end_date = conversation_end_date
        self.data_type = data_type
        self.ej_user_token = ""
        self.ej_user_auth = {"email": "contato@pencillabs.com.br", "name": "Pencillabs"}

    def execute(self, context):
        self.set_connections()
        self.authenticate()
        conversation_votes_endpoint = self.get_conversation_votes_endpoint()
        votes = self.get_conversation_votes(conversation_votes_endpoint)
        self.save(votes)

    def set_connections(self):
        self.connection = BaseHook.get_connection("ej_dev_api")
        self.ej_host_url = f"{self.connection.schema}://{self.connection.host}"
        self.ej_rest_registration_endpoint = (
            f"{self.ej_host_url}/rest-auth/registration/"
        )

    def get_conversation_votes_endpoint(self):
        filter_by_date = self.get_query_params_filter()
        return f"{self.ej_host_url}/api/v1/conversations/{self.conversation_id}/votes?{filter_by_date}"

    def authenticate(self):
        response = self.request(
            self.ej_rest_registration_endpoint, "post", self.ej_user_auth, {}
        )
        self.ej_user_token = response.get("key")

    def get_conversation_votes(self, url):
        return self.request(
            url,
            "get",
            {},
            {"Authorization": f"Token {self.ej_user_token}"},
        )

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

    def get_query_params_filter(self):
        if not (self.conversation_start_date and self.conversation_end_date):
            end_date = datetime.datetime.now().strftime("%Y-%m-%d")
            start_date = (
                datetime.datetime.now() - datetime.timedelta(days=1)
            ).strftime("%Y-%m-%d")
            return f"startDate={start_date}&endDate={end_date}"
        return f"startDate={self.conversation_start_date}&endDate={self.conversation_end_date}"

    def save(self, data):
        file_name = f"{self.data_type}.json"
        with open(f"/tmp/{file_name}", "w") as f:
            f.write(json.dumps(data))

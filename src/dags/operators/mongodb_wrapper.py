import os
from pymongo import MongoClient
import json


class MongodbWrapper:
    def __init__(self) -> None:
        client_variables = self.get_mongodb_connection_variables()
        client = MongoClient(
            client_variables["DB_HOST"],
            client_variables["DB_PORT"],
            username=client_variables["DB_USERNAME"],
            password=client_variables["DB_PASSWORD"],
        )
        self.client = MongoClient("mongo", 27017, username="mongo", password="mongo")

    def save_votes(self, votes_dataframe):
        if not votes_dataframe.empty:
            votes = json.loads(votes_dataframe.to_json(orient="records"))
            conversations = self.client.admin.conversations
            conversations.insert_many(votes)

    def get_mongodb_connection_variables(self):
        return {
            "DB_HOST": os.getenv("MONGODB_ANALYSIS_HOST", "localhost"),
            "DB_PORT": int(os.getenv("MONGODB_ANALYSIS_PORT", 27017)),
            "DB_USERNAME": os.getenv("MONGODB_ANALYSIS_USERNAME", "mongo"),
            "DB_PASSWORD": os.getenv("MONGODB_ANALYSIS_PASSWORD", "mongo"),
        }

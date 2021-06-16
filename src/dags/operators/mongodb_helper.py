from pymongo import MongoClient
import json


class MongodbHelper:
    def __init__(self) -> None:
        self.client = MongoClient("mongo", 27017, username="mongo", password="mongo")

    def save_votes(self, votes_dataframe):
        votes = json.loads(votes_dataframe.to_json(orient="records"))
        conversations = self.client.admin.conversations
        conversations.insert_many(votes)

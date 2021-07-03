import os
import json
import datetime
import pandas as pd
import time
import json
import requests
from dateutil.parser import *
from dateutil.tz import tzlocal

from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.hooks.base_hook import BaseHook
from .lib.analytics_client import AnalyticsClient
from .lib.mongodb_wrapper import MongodbWrapper


class AnalyticsApiOperator(BaseOperator):

    template_fields = (
        "conversation_start_date",
        "conversation_end_date",
        "analytics_view_id",
    )

    def __init__(
        self,
        conversation_start_date: str,
        conversation_end_date: str,
        analytics_view_id: str,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.conversation_start_date = conversation_start_date
        self.conversation_end_date = conversation_end_date
        self.analytics_view_id = analytics_view_id

    def execute(self, context):
        try:
            self.votes_df = pd.read_json("/opt/airflow/data/votes.json")
        except:
            pass
        self.analytics_client = AnalyticsClient()
        self.mongodb_wrapper = MongodbWrapper()
        self.merge_with_analytics()
        self.mongodb_wrapper.save_votes(self.votes_dataframe)

    def vote_belongs_to_activity(self, voteTimestamp, activityTimestamp):
        """
        Checks if a vote was created by a activity by comparing their timestamps.
        if timezone_activity + delta is bigger then voteTimestamp, we assume that the vote was created by the activity.
        """
        # voteTimestamp is a naive timestamp. timezone_vote is a datetime with tzlocal zone
        timezone_vote = datetime.datetime.fromtimestamp(
            voteTimestamp / 1000, tz=tzlocal()
        )
        timezone_activity = parse(activityTimestamp)
        delta = datetime.timedelta(minutes=10)
        return timezone_activity + delta >= timezone_vote

    def get_gid_votes(self, _id):
        return self.votes_dataframe[
            self.votes_dataframe.author__metadata__analytics_id == _id
        ]["created"]

    def get_gid_activities(self, gid):
        if not gid or gid == "1":
            return []
        report = self.analytics_client.get_user_activity(
            self.analytics_view_id,
            gid,
            self.conversation_start_date,
            self.conversation_end_date,
        )
        return self.get_sessions_activities(report["sessions"])

    def get_sessions_activities(self, sessions):
        sessions_activities = list(map(lambda session: session["activities"], sessions))
        activities = []
        list(map(lambda x: activities.append(x.pop()), sessions_activities))
        return activities

    def merge_ej_and_analytics(self, activity, voteTime, gid):
        df = self.votes_dataframe
        df.loc[
            (df["created"] == voteTime) & (df.author__metadata__analytics_id == gid),
            "analytics_source",
        ] = activity["source"]
        df.loc[
            (df["created"] == voteTime) & (df.author__metadata__analytics_id == gid),
            "analytics_medium",
        ] = activity["medium"]
        df.loc[
            (df["created"] == voteTime) & (df.author__metadata__analytics_id == gid),
            "analytics_pageview",
        ] = activity["pageview"]["pagePath"]
        df.loc[
            (df["created"] == voteTime) & (df.author__metadata__analytics_id == gid),
            "analytics_campaign",
        ] = activity["campaign"]
        return df

    def merge_with_analytics(self):
        self.votes_dataframe = pd.DataFrame(self.votes_df)
        if not self.votes_dataframe.empty:
            gids = (
                self.votes_dataframe.author__metadata__analytics_id.value_counts().keys()
            )
            print(f"{len(gids)} GIDS TO PROCESS")
            for idx, gid in enumerate(gids):
                try:
                    gidActivities = self.get_gid_activities(gid)
                    gidVotesTimestamps = self.get_gid_votes(gid)
                    for activity in gidActivities:
                        for vote_timestamp in gidVotesTimestamps:
                            belongs = self.vote_belongs_to_activity(
                                vote_timestamp, activity["activityTime"]
                            )
                            if belongs:
                                self.votes_dataframe = self.merge_ej_and_analytics(
                                    activity, vote_timestamp, gid
                                )
                except Exception as err:
                    print(err)
                    pass
                if idx % 100 == 0:
                    print(f"{idx} GIDS processed")

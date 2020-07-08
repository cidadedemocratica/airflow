import os
import json
import datetime
import pandas as pd
import time
import json
import requests
from dateutil.parser import *

from src import analytics_api as analytics
from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.hooks.base_hook import BaseHook
from src.airflow.operators import helper


class AnalyticsApiOperator(BaseOperator):

    @apply_defaults
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.votes_df = pd.read_json('/tmp/votes_and_mautic.json')
        self.helper = helper.OperatorHelper()
        self.analytics_client = analytics.initialize_analyticsreporting()

    def execute(self, context):
        self.merge_with_analytics()

    def vote_belongs_to_activity(self, voteCreatedTime, activityTime):
        # Votes from EJ, are in utc date format, activities from analytics are not.
        # We will have to parse all to utc (better solution).
        # For a quick fix, we subtract three hours from vote date, to match Sao Paulo timzone.
        utc_vote_date = parse(voteCreatedTime) - datetime.timedelta(hours=3)
        utc_offeset_timedelta = datetime.datetime.utcnow() - datetime.datetime.now()
        utc_activity_time = parse(activityTime) + utc_offeset_timedelta
        deltaDate = utc_activity_time + datetime.timedelta(minutes=5)
        return utc_vote_date < deltaDate and utc_vote_date >= utc_activity_time

    def get_client_votes(self, _id):
        return self.votes_dataframe[self.votes_dataframe['gid'] == _id]["criado"]

    def merge_with_analytics(self):
        self.votes_dataframe = pd.DataFrame(self.votes_df)
        gids = pd.DataFrame(self.votes_df).groupby(
            'gid').count().reset_index(level=0)

        for counter, row in enumerate(gids.loc()):
            gid = row["gid"]
            if(not gid or gid == '1'):
                continue
            self.helper.wait_analytics_quota(counter, "votes")
            report = analytics.get_report(
                self.analytics_client, gid)
            activities = self.helper.get_sessions_activities(
                report['sessions'])
            for activity in activities:
                voteTimeStamps = self.get_client_votes(gid)
                for voteTime in voteTimeStamps:
                    belongs = self.vote_belongs_to_activity(
                        voteTime, activity['activityTime'])
                    if(belongs):
                        self.votes_dataframe = self.helper.update_df_with_activity(
                            self.votes_dataframe, activity, voteTime, gid)
                        self.votes_dataframe.to_json(
                            '/tmp/votes_analytics_mautic.json')
            if(counter == len(gids) - 1):
                break

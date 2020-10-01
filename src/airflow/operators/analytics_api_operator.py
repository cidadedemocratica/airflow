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
        try:
            self.votes_df = pd.read_json('/tmp/votes.json')
        except:
            pass
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

    def get_gid_votes(self, _id):
        return self.votes_dataframe[self.votes_dataframe.author__metadata__analytics_id == _id]["criado"]

    def get_gid_activities(self, gid):
        if(not gid or gid == '1'):
            return []
        report = analytics.get_user_activity(
            self.analytics_client, gid)
        return self.get_sessions_activities(report['sessions'])

    def get_sessions_activities(self, sessions):
        sessions_activities = list(map(
            lambda session: session['activities'], sessions))
        activities = []
        list(map(lambda x: activities.append(x.pop()), sessions_activities))
        return activities

    def update_df_with_activity(self, activity, voteTime, gid):
        df = self.votes_dataframe
        df.loc[(df['criado'] == voteTime) & (df.author__metadata__analytics_id == gid),
               'analytics_source'] = activity['source']
        df.loc[(df['criado'] == voteTime) & (df.author__metadata__analytics_id == gid),
               'analytics_medium'] = activity['medium']
        df.loc[(df['criado'] == voteTime) & (df.author__metadata__analytics_id == gid),
               'analytics_pageview'] = activity['pageview']['pagePath']
        df.loc[(df['criado'] == voteTime) & (df.author__metadata__analytics_id == gid),
               'analytics_campaign'] = activity['campaign']
        return df

    def merge_with_analytics(self):
        self.votes_dataframe = pd.DataFrame(self.votes_df)
        gids = self.votes_dataframe.author__metadata__analytics_id.value_counts().keys()

        print(f"{len(gids)} GIDS TO PROCESS")
        for idx, gid in enumerate(gids):
            activities = self.get_gid_activities(gid)
            voteTimeStamps = self.get_gid_votes(gid)
            for activity in activities:
                for voteTime in voteTimeStamps:
                    belongs = self.vote_belongs_to_activity(
                        voteTime, activity['activityTime'])
                    if(belongs):
                        self.votes_dataframe = self.update_df_with_activity(
                            activity, voteTime, gid)
            self.votes_dataframe.to_json('/tmp/votes_analytics.json')
            if(idx % 100 == 0):
                print(f'{idx} GIDS processed')

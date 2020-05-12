from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
from dateutil.parser import *
from src import analytics_api as analytics
import os
import json
import datetime
import re
import pandas as pd
import time
from airflow.utils.dates import days_ago


class EjOperator(BaseOperator):

    @apply_defaults
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.analytics = analytics.initialize_analyticsreporting()
        self.df1 = None
        self.WAIT_ANALYTICS_QUOTA = 99

    def execute(self, context):
        ej_mautic_analytics = self.merge_ej_mautic_analytics(context)
        self.merge_analytics_activities(ej_mautic_analytics)
        return 'DataFrame with EJ, Mautic and Analytics data, generated on /tmp/ej_analytics_mautic.csv'

    def vote_created_by_activity(self, voteCreatedTime, activityTime):
        # Votes from EJ, are in utc date format, activities from analytics are not.
        # We will have to parse all to utc (better solution).
        # For a quick fix, we subtract three hours from vote date, to match Sao Paulo timzone.
        utc_vote_date = parse(voteCreatedTime) - datetime.timedelta(hours=3)
        utc_offeset_timedelta = datetime.datetime.utcnow() - datetime.datetime.now()
        # utc_activity_time = parse(
        #    activityTime) + utc_offeset_timedelta + datetime.timedelta(hours=4)
        utc_activity_time = parse(activityTime) + utc_offeset_timedelta
        deltaDate = utc_activity_time + datetime.timedelta(minutes=5)
        return utc_vote_date < deltaDate and utc_vote_date >= utc_activity_time

    def get_ej_votes_from_xcom(self, context):
        return json.loads(context['task_instance'].xcom_pull(
            task_ids='request_ej_reports_data'))

    def get_mautic_contacts_from_xcom(self, context):
        return json.loads(context['task_instance'].xcom_pull(
            task_ids='request_mautic_data'))["contacts"]

    def get_mtc_id_from_email(self, email):
        return email.split('-')[0]

    def get_email_sufix(self, email):
        return email.split('-')[1]

    def voter_is_a_mautic_contact(self, vote):
        if(len(vote["email"].split('-')) > 1):
            email_sufix = self.get_email_sufix(vote["email"])
            if(email_sufix == 'mautic@mail.com'):
                return True
        return False

    def get_analytics_ga(self, contacts, mtc_id):
        return contacts[mtc_id]["fields"]["core"]["gid"]["value"]

    def parse_ga(self, _ga):
        return re.sub(r"^GA[0-9]*\.[0-9]*\.*", "", _ga)

    def merge(self, contact, vote, _ga):
        _gaValue = self.parse_ga(_ga)
        mautic_email = contact["fields"]["core"]["email"]["value"]
        first_name = contact["fields"]["core"]["firstname"]["value"]
        last_name = contact["fields"]["core"]["lastname"]["value"]
        return {**vote, **{"analytics_client_id": _gaValue,
                           "mautic_email": mautic_email,
                           "mautic_first_name": first_name,
                           "mautic_last_name": last_name}}

    def update_df_with_activity(self, activity, _id):
        self.df1.loc[self.df1['analytics_client_id'] == _id,
                     'analytics_source'] = activity['source']
        self.df1.loc[self.df1['analytics_client_id'] ==
                     _id, 'analytics_medium'] = activity['medium']
        self.df1.loc[self.df1['analytics_client_id'] ==
                     _id, 'analytics_pageview'] = activity['pageview']['pagePath']
        self.df1.loc[self.df1['analytics_client_id'] ==
                     _id, 'analytics_campaign'] = activity['campaign']
        self.df1.to_csv('/tmp/ej_analytics_mautic.csv')

    def get_sessions_activities(self, sessions):
        sessions_activities = list(map(
            lambda session: session['activities'], sessions))
        activities = []
        list(map(lambda x: activities.append(x.pop()), sessions_activities))
        return activities

    def get_client_votes(self, _id):
        return self.df1[self.df1['analytics_client_id'] == _id]["criado"]

    def wait_analytics_quota(self, analytics_requests):
        print("COUNTER :", analytics_requests)
        if(analytics_requests % self.WAIT_ANALYTICS_QUOTA == 0 and analytics_requests > 0):
            print(f"{analytics_requests} analytics clients processed")
            print("WAITING ANALYTICS QUOTA")
            time.sleep(120)

    # from _ga key, retrieve _ga activities, and merge with vote.
    # Analytics activities has informations like the source, medium and pages accessed by user.
    def merge_analytics_activities(self, ej_mautic_analytics):
        if ej_mautic_analytics:
            self.df1 = pd.DataFrame(ej_mautic_analytics)
            for counter, _id in enumerate(self.df1['analytics_client_id']):
                self.wait_analytics_quota(counter)
                report = analytics.get_report(self.analytics, _id)
                activities = self.get_sessions_activities(report['sessions'])
                for activity in activities:
                    voteTimeStamps = self.get_client_votes(_id)
                    for voteTime in voteTimeStamps:
                        created = self.vote_created_by_activity(
                            voteTime, activity['activityTime'])
                        if(created):
                            self.update_df_with_activity(activity, _id)

    # Merge, on a single dictionary, ej, mautic and analytics _ga key.
    def merge_ej_mautic_analytics(self, context):
        ej_votes = self.get_ej_votes_from_xcom(context)
        mautic_contacts = self.get_mautic_contacts_from_xcom(context)
        list_of_mautic_contacts_ids = list(mautic_contacts)
        ej_mautic_analytics = []
        valid_mtc_ids = set({})
        invalid_mtc_ids = set({})
        for vote in ej_votes:
            if(self.voter_is_a_mautic_contact(vote)):
                mtc_id = self.get_mtc_id_from_email(vote["email"])
                if(mtc_id in list_of_mautic_contacts_ids):
                    valid_mtc_ids.add(mtc_id)
                    _ga = self.get_analytics_ga(mautic_contacts, mtc_id)
                    if(_ga):
                        compiled_data = self.merge(
                            mautic_contacts[mtc_id], vote, _ga)
                        ej_mautic_analytics.append(compiled_data)
                else:
                    invalid_mtc_ids.add(mtc_id)
        return ej_mautic_analytics

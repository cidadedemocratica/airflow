from src import analytics_api as analytics
from src.operators import helper
import pandas as pd
import datetime
from dateutil.parser import *


class VotesCompiler():

    def __init__(self, analytics_client):
        self.votes_dataframe = None
        self.helper = helper.OperatorHelper()
        self.analytics_client = analytics_client

    def compile(self, ej_votes, mautic_contacts):
        votes_mautic_analytics = []
        list_of_mautic_contacts_ids = list(mautic_contacts)
        for vote in ej_votes:
            if(self.voter_is_a_mautic_contact(vote)):
                mtc_id = self.helper.get_mtc_id_from_email(vote["email"])
                if(mtc_id in list_of_mautic_contacts_ids):
                    _ga = self.helper.get_contact_ga(mautic_contacts, mtc_id)
                    if(_ga):
                        compiled_data = self.helper.merge(
                            mautic_contacts[mtc_id], vote, _ga)
                        votes_mautic_analytics.append(compiled_data)
        return votes_mautic_analytics

    def voter_is_a_mautic_contact(self, vote):
        if(len(vote["email"].split('-')) > 1):
            email_sufix = self.helper.get_email_sufix(vote["email"])
            if(email_sufix == 'mautic@mail.com'):
                return True
        return False

    def get_client_votes(self, _id):
        return self.votes_dataframe[self.votes_dataframe['analytics_client_id'] == _id]["criado"]

    def vote_created_by_activity(self, voteCreatedTime, activityTime):
        # Votes from EJ, are in utc date format, activities from analytics are not.
        # We will have to parse all to utc (better solution).
        # For a quick fix, we subtract three hours from vote date, to match Sao Paulo timzone.
        utc_vote_date = parse(voteCreatedTime) - datetime.timedelta(hours=3)
        utc_offeset_timedelta = datetime.datetime.utcnow() - datetime.datetime.now()
        utc_activity_time = parse(activityTime) + utc_offeset_timedelta
        deltaDate = utc_activity_time + datetime.timedelta(minutes=5)
        return utc_vote_date < deltaDate and utc_vote_date >= utc_activity_time

    def merge_with_analytics(self, data):
        if data:
            self.votes_dataframe = pd.DataFrame(data)
            for counter, _id in enumerate(self.votes_dataframe['analytics_client_id']):
                self.helper.wait_analytics_quota(counter, "votes")
                report = analytics.get_report(self.analytics_client, _id)
                activities = self.helper.get_sessions_activities(
                    report['sessions'])
                for activity in activities:
                    voteTimeStamps = self.get_client_votes(_id)
                    for voteTime in voteTimeStamps:
                        created = self.vote_created_by_activity(
                            voteTime, activity['activityTime'])
                        if(created):
                            self.votes_dataframe = self.helper.update_df_with_activity(
                                self.votes_dataframe, activity, _id)
                            self.votes_dataframe.to_csv(
                                '/tmp/votes_analytics_mautic.csv')

from src import analytics_api as analytics
from src.operators import helper
import pandas as pd
import datetime
from dateutil.parser import *


class CommentsCompiler():

    def __init__(self, analytics_client):
        self.comments_dataframe = None
        self.analytics_client = analytics_client
        self.helper = helper.OperatorHelper()

    def compile(self, ej_comments, mautic_contacts):
        comments_mautic_analytics = []
        list_of_mautic_contacts_ids = list(mautic_contacts)
        for comment in ej_comments:
            if(self.commentator_is_a_mautic_contact(comment)):
                mtc_id = self.helper.get_mtc_id_from_email(comment["autor"])
                if(mtc_id in list_of_mautic_contacts_ids):
                    _ga = self.helper.get_analytics_ga(mautic_contacts, mtc_id)
                    if(_ga):
                        compiled_data = self.helper.merge(
                            mautic_contacts[mtc_id], comment, _ga)
                        comments_mautic_analytics.append(compiled_data)
        return comments_mautic_analytics

    def commentator_is_a_mautic_contact(self, comment):
        if(len(comment["autor"].split('-')) > 1):
            email_sufix = self.helper.get_email_sufix(comment["autor"])
            if(email_sufix == 'mautic@mail.com'):
                return True
        return False

    def merge_with_analytics(self, data):
        if data:
            self.comments_dataframe = pd.DataFrame(data)
            for counter, _id in enumerate(self.comments_dataframe['analytics_client_id']):
                self.helper.wait_analytics_quota(counter, "comments")
                report = analytics.get_report(self.analytics_client, _id)
                activities = self.helper.get_sessions_activities(
                    report['sessions'])
                for activity in activities:
                    commentsTimeStamps = self.get_client_comments_timestamps(
                        _id)
                    for commentTime in commentsTimeStamps:
                        created = self.comment_created_by_activity(
                            commentTime, activity['activityTime'])
                        if(created):
                            self.comments_dataframe = self.helper.update_df_with_activity(
                                self.comments_dataframe, activity, _id)
                            self.comments_dataframe.to_csv(
                                '/tmp/comments_analytics_mautic.csv')

    def get_client_comments_timestamps(self, _id):
        return self.comments_dataframe[self.comments_dataframe['analytics_client_id'] == _id]["criado"]

    def comment_created_by_activity(self, commentCreatedTime, activityTime):
        # Comments from EJ, are in utc date format, activities from analytics are not.
        # We will have to parse all to utc (better solution).
        # For a quick fix, we subtract three hours from commentsdate, to match Sao Paulo timzone.
        utc_comment_date = parse(commentCreatedTime) - \
            datetime.timedelta(hours=3)
        utc_offeset_timedelta = datetime.datetime.utcnow() - datetime.datetime.now()
        utc_activity_time = parse(activityTime) + utc_offeset_timedelta
        deltaDate = utc_activity_time + datetime.timedelta(minutes=5)
        return utc_comment_date < deltaDate and utc_comment_date >= utc_activity_time

import re
import time


class OperatorHelper():

    def __init__(self):
        self.MAX_REQUESTS_PER_TURN = 99
        self.TIME_TO_WAIT_ANALYTICS_QUOTA = 300

    def parse_ga(self, _ga):
        return re.sub(r"^GA[0-9]*\.[0-9]*\.*", "", _ga)

    def merge(self, contact, data, _ga):
        _gaValue = self.parse_ga(_ga)
        mautic_email = contact["fields"]["core"]["email"]["value"]
        first_name = contact["fields"]["core"]["firstname"]["value"]
        last_name = contact["fields"]["core"]["lastname"]["value"]
        return {**data, **{"analytics_client_id": _gaValue,
                           "mautic_email": mautic_email,
                           "mautic_first_name": first_name,
                           "mautic_last_name": last_name}}

    def get_email_sufix(self, email):
        return email.split('-')[1]

    def get_mtc_id_from_email(self, email):
        return email.split('-')[0]

    def get_contact_ga(self, contacts, mtc_id):
        return contacts[mtc_id]["fields"]["core"]["gid"]["value"]

    def get_sessions_activities(self, sessions):
        sessions_activities = list(map(
            lambda session: session['activities'], sessions))
        activities = []
        list(map(lambda x: activities.append(x.pop()), sessions_activities))
        return activities

    def wait_analytics_quota(self, analytics_requests, data_type):
        if(analytics_requests % self.MAX_REQUESTS_PER_TURN == 0 and analytics_requests > 0):
            print(f"{analytics_requests} analytics clients processed for {data_type}")
            print("WAITING ANALYTICS QUOTA")
            time.sleep(self.TIME_TO_WAIT_ANALYTICS_QUOTA)

    def update_df_with_activity(self, df, activity, _id):
        df.loc[df['analytics_client_id'] == _id,
               'analytics_source'] = activity['source']
        df.loc[df['analytics_client_id'] ==
               _id, 'analytics_medium'] = activity['medium']
        df.loc[df['analytics_client_id'] ==
               _id, 'analytics_pageview'] = activity['pageview']['pagePath']
        df.loc[df['analytics_client_id'] ==
               _id, 'analytics_campaign'] = activity['campaign']
        return df

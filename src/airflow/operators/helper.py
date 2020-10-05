import re
import time


class OperatorHelper():

    def __init__(self):
        self.MAX_REQUESTS_PER_TURN = 10
        self.TIME_TO_WAIT_ANALYTICS_QUOTA = 3

    def parse_ga(self, _ga):
        return re.sub(r"^GA[0-9]*\.[0-9]*\.*", "", _ga)

    def get_email_sufix(self, email):
        return email.split('-')[1]

    def get_mtc_id_from_email(self, email):
        if(len(email.split('-')) > 1 and email.split('-')[1] == 'mautic@mail.com'):
            return email.split('-')[0]
        return ""

    def get_contact_ga(self, contacts, mtc_id):
        return contacts[mtc_id]["fields"]["core"]["gid"]["value"]

    def wait_analytics_quota(self, analytics_requests, data_type):
        if(analytics_requests % self.MAX_REQUESTS_PER_TURN == 0 and analytics_requests > 0):
            print(f"{analytics_requests} gids processed")
            time.sleep(self.TIME_TO_WAIT_ANALYTICS_QUOTA)

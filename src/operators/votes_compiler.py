from src.operators import helper


class VotesCompiler():

    def __init__(self):
        self.helper = helper.OperatorHelper()

    def compile(self, ej_votes, mautic_contacts):
        ej_mautic_analytics = []
        valid_mtc_ids = set({})
        invalid_mtc_ids = set({})
        list_of_mautic_contacts_ids = list(mautic_contacts)
        for vote in ej_votes:
            if(self.voter_is_a_mautic_contact(vote)):
                mtc_id = self.get_mtc_id_from_email(vote["email"])
                if(mtc_id in list_of_mautic_contacts_ids):
                    valid_mtc_ids.add(mtc_id)
                    _ga = self.get_analytics_ga(mautic_contacts, mtc_id)
                    if(_ga):
                        compiled_data = self.helper.merge(
                            mautic_contacts[mtc_id], vote, _ga)
                        ej_mautic_analytics.append(compiled_data)
                else:
                    invalid_mtc_ids.add(mtc_id)
        return ej_mautic_analytics

    def get_email_sufix(self, email):
        return email.split('-')[1]

    def voter_is_a_mautic_contact(self, vote):
        if(len(vote["email"].split('-')) > 1):
            email_sufix = self.get_email_sufix(vote["email"])
            if(email_sufix == 'mautic@mail.com'):
                return True
        return False

    def get_mtc_id_from_email(self, email):
        return email.split('-')[0]

    def get_analytics_ga(self, contacts, mtc_id):
        return contacts[mtc_id]["fields"]["core"]["gid"]["value"]

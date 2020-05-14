import re


class OperatorHelper():

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


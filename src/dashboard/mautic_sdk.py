import requests
import os


class MauticSdk():

    def __init__(self):
        self.mautic_host = "https://comunidade.transparenciainternacional.org.br/api/contacts"
        self.mautic_headers = {
            "Authorization": f'Basic cmljYXJkb0BjaWRhZGVkZW1vY3JhdGljYS5vcmcuYnI6cVlVNjQzNHJPRjNQ'}

    def get_contact_email(self, email):
        if(len(email.split('-')) > 1 and email.split('-')[1] == 'mautic@mail.com'):
            mtc_id = email.split('-')[0]
            response = requests.get(
                f"{self.mautic_host}/{mtc_id}", headers=self.mautic_headers)
            contact = response.json()['contact']
            return contact.get('fields').get('all').get('email')
        return email

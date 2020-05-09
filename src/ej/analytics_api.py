"""Hello Analytics Reporting API V4."""

from pathlib import Path  # python3 only
import os
import argparse

from apiclient.discovery import build
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools
import datetime

from dotenv import load_dotenv
from pathlib import Path
CURRENT_ENV = os.getenv('AIRFLOW_ENV', 'prod')
env_path = Path('.') / f"/tmp/.{CURRENT_ENV}.env"
load_dotenv(dotenv_path=env_path)

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
# Path to client_secrets.json file.
CLIENT_SECRETS_PATH = '/tmp/client_secrets.json'
VIEW_ID = os.getenv("VIEW_ID")


def initialize_analyticsreporting():
    """Initializes the analyticsreporting service object.

    Returns:
      analytics an authorized analyticsreporting service object.
    """
    # Parse command-line arguments.
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[tools.argparser])
    flags = parser.parse_args([])

    # Set up a Flow object to be used if we need to authenticate.
    flow = client.flow_from_clientsecrets(
        CLIENT_SECRETS_PATH, scope=SCOPES,
        message=tools.message_if_missing(CLIENT_SECRETS_PATH))

    # Prepare credentials, and authorize HTTP object with them.
    # If the credentials don't exist or are invalid run through the native client
    # flow. The Storage object will ensure that if successful the good
    # credentials will get written back to a file.
    storage = file.Storage(
        f"{os.getenv('AIRFLOW_HOME')}/.analyticsreporting.dat")
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage, flags)
    http = credentials.authorize(http=httplib2.Http())

    # Build the service object.
    analytics = build('analyticsreporting', 'v4',
                      http=http, cache_discovery=False)

    return analytics


def get_report(analytics, userID):
    # start from datetime.now - 60 days
    startDate = (datetime.datetime.now(datetime.timezone.utc) -
                 datetime.timedelta(days=60)).strftime("%Y-%m-%d")
    # include today on report
    endDate = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    return analytics.userActivity().search(
        body={
            "viewId": VIEW_ID,
            "user": {
                "type": "CLIENT_ID",
                "userId": userID
            },
            "dateRange": {
                "startDate": startDate,
                "endDate": endDate}
        }
    ).execute()


def print_response(response):
    """Parses and prints the Analytics Reporting API V4 response"""

    for report in response.get('reports', []):
        columnHeader = report.get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = columnHeader.get(
            'metricHeader', {}).get('metricHeaderEntries', [])
        rows = report.get('data', {}).get('rows', [])

        for row in rows:
            dimensions = row.get('dimensions', [])
            dateRangeValues = row.get('metrics', [])

            for header, dimension in zip(dimensionHeaders, dimensions):
                print(header + ': ' + dimension)

            for i, values in enumerate(dateRangeValues):
                print('Date range (' + str(i) + ')')
                for metricHeader, value in zip(metricHeaders, values.get('values')):
                    print(metricHeader.get('name') + ': ' + value)

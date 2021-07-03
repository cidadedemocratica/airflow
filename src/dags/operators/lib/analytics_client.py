"""Hello Analytics Reporting API V4."""

import os
import re
import datetime

from pathlib import Path  # python3 only
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path

CURR_DIR = os.path.dirname(os.path.realpath(__file__))
CLIENT_SECRETS_PATH = CURR_DIR + "/client_secrets.json"
SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]


class AnalyticsClient:
    def __init__(self) -> None:
        self.analytics = self._initialize_analyticsreporting()

    def get_user_activity(self, view_id, userID, start_date, end_date):
        if not (start_date and end_date):
            start_date = (
                datetime.datetime.now(datetime.timezone.utc)
                - datetime.timedelta(days=90)
            ).strftime("%Y-%m-%d")
            end_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
        return (
            self.analytics.userActivity()
            .search(
                body={
                    "viewId": view_id,
                    "user": {
                        "type": "CLIENT_ID",
                        "userId": re.sub(r"^[a-zA-Z0-9]*\.[a-zA-Z0-9]*\.", "", userID),
                    },
                    "dateRange": {"startDate": start_date, "endDate": end_date},
                }
            )
            .execute()
        )

    def _initialize_analyticsreporting(self):
        """Initializes the analyticsreporting service object.

        Returns:
        analytics an authorized analyticsreporting service object.
        """
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CLIENT_SECRETS_PATH, SCOPES
        )
        analytics = build("analyticsreporting", "v4", credentials=credentials)
        return analytics

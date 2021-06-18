import os
import json
import datetime
import pandas as pd
import time
import json
import requests

from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.hooks.base_hook import BaseHook


class MergeAnalyticsMauticOperator(BaseOperator):
    @apply_defaults
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def execute(self, context):
        try:
            votes_analytics = pd.read_json("/tmp/votes_analytics.json")
            votes_mautic = pd.read_json("/tmp/votes_mautic.json")
            df = pd.concat(
                [
                    votes_analytics,
                    pd.DataFrame(
                        votes_mautic,
                        columns=["mtc_email", "mtc_first_name", "mtc_last_name"],
                    ),
                ],
                axis=1,
            )
            df.to_json("/tmp/votes_analytics_mautic.json")
        except:
            print("could not merge votes_analytics.json and votes_mautic.json")

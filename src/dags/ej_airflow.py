import os
import json
import datetime
import re
import pandas as pd

from operators import (
    EjApiOperator,
    AnalyticsApiOperator,
)
from airflow.models import DAG
from dotenv import load_dotenv
from pathlib import Path

CURRENT_ENV = os.getenv("AIRFLOW_ENV", "prod")
env_path = Path(".") / f"/tmp/.{CURRENT_ENV}.env"
load_dotenv(dotenv_path=env_path)

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime.datetime.now(tz=datetime.timezone.utc)
    + datetime.timedelta(hours=-1),
    "email": ["airflow@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "schedule_interval": "@daily",
}

with DAG("ej_analysis_dag", default_args=default_args) as dag:
    t1 = EjApiOperator(
        task_id="request_conversation_votes",
        conversation_id="{{ dag_run.conf.get('conversation_id') }}",
        conversation_start_date="{{ dag_run.conf.get('conversation_start_date') or '' }}",
        conversation_end_date="{{ dag_run.conf.get('conversation_end_date') or '' }}",
        data_type="votes",
    )

    t2 = AnalyticsApiOperator(
        task_id="merge_votes_with_analytics",
        conversation_start_date="{{ dag_run.conf.get('conversation_start_date') or '' }}",
        conversation_end_date="{{ dag_run.conf.get('conversation_end_date') or '' }}",
        analytics_view_id="{{ dag_run.conf.get('analytics_view_id') or '' }}"
    )

    t1 >> t2

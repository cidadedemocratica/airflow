import os
import json
import datetime
import re
import pandas as pd

from operators import EjApiOperator, MauticApiOperator, AnalyticsApiOperator, MergeAnalyticsMauticOperator
from airflow.models import DAG
from dotenv import load_dotenv
from pathlib import Path

CURRENT_ENV = os.getenv('AIRFLOW_ENV', 'prod')
env_path = Path('.') / f"/tmp/.{CURRENT_ENV}.env"
load_dotenv(dotenv_path=env_path)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=-1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'schedule_interval': None
}

with DAG('ej_analysis_dag', default_args=default_args) as dag:
    t1 = EjApiOperator(
        task_id="request_conversation_votes",
        conversation_id="{{ dag_run.conf['conversation_id'] }}",
        data_type="votes")

    #t4 = MauticApiOperator(
    #    task_id="merge_votes_with_mautic",
    #    dag=dag)

    t2 = AnalyticsApiOperator(task_id="merge_votes_with_analytics")

    #t6 = MergeAnalyticsMauticOperator(
    #    task_id="merge_analytics_mautic",
    #    dag=dag
    #)

    t1 >> t2
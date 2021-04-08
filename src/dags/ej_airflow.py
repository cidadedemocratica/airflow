import os
import json
import datetime
import re
import pandas as pd

from airflow.utils.dates import days_ago
from operators import EjApiOperator, MauticApiOperator, AnalyticsApiOperator, MergeAnalyticsMauticOperator
from airflow.models import DAG
from dateutil.parser import *
from dotenv import load_dotenv
from pathlib import Path

CURRENT_ENV = os.getenv('AIRFLOW_ENV', 'prod')
env_path = Path('.') / f"/tmp/.{CURRENT_ENV}.env"
load_dotenv(dotenv_path=env_path)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.datetime.now() - datetime.timedelta(minutes=10),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0
}

dag = DAG('ej_analysis_dag', default_args=default_args)

t1 = EjApiOperator(
    task_id="request_conversation_votes",
    conversation_id=64,
    data_type="votes",
    dag=dag)

t2 = EjApiOperator(
    task_id="request_conversation_comments",
    conversation_id=64,
    data_type="comments",
    dag=dag)

t3 = EjApiOperator(
    task_id="request_conversation_clusters",
    conversation_id=64,
    data_type="clusters",
    dag=dag)

t4 = MauticApiOperator(
    task_id="merge_votes_with_mautic",
    dag=dag)

t5 = AnalyticsApiOperator(
    task_id="merge_votes_with_analytics",
    dag=dag)

t6 = MergeAnalyticsMauticOperator(
    task_id="merge_analytics_mautic",
    dag=dag
)

t1 >> [t5, t4] >> t6
t2, t3

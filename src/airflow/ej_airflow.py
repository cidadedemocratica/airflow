from airflow.models import DAG
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.operators.python_operator import PythonOperator
from dateutil.parser import *
from src import analytics_api as analytics
import os
import json
import datetime
import re
import pandas as pd
from airflow.utils.dates import days_ago
from src.airflow.operators import EjOperator
from src.airflow.operators import EjApiOperator

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

dag = DAG('osf_pipeline', default_args=default_args)

t1 = EjApiOperator(
    task_id="request_conversation_votes",
    conversation_id=56,
    data_type="votes",
    log_response=True,
    dag=dag)

t2 = EjApiOperator(
    task_id="request_conversation_comments",
    conversation_id=56,
    data_type="comments",
    log_response=True,
    dag=dag)

[t1, t2]

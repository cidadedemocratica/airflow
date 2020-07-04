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

t1 = SimpleHttpOperator(
    task_id="request_ej_votes",
    http_conn_id=os.getenv("ej_conn_id"),
    endpoint=f'/api/v1/conversations/{os.getenv("CONVERSATION_ID")}/reports?fmt=json&&export=votes',
    method="GET",
    headers={"Accept": "text/csv"},
    response_check=lambda response: True if response.content else False,
    log_response=True,
    xcom_push=True,
    dag=dag)

t2 = SimpleHttpOperator(
    task_id="request_ej_comments",
    http_conn_id=os.getenv("ej_conn_id"),
    endpoint=f'/api/v1/conversations/{os.getenv("CONVERSATION_ID")}/reports?fmt=json&&export=comments',
    method="GET",
    headers={"Accept": "text/csv"},
    response_check=lambda response: True if response.content else False,
    log_response=True,
    xcom_push=True,
    dag=dag)


t3 = SimpleHttpOperator(
    task_id="request_mautic_contacts",
    http_conn_id=os.getenv("mautic_conn_id"),
    endpoint='/api/contacts?search=gid:GA&limit=300',
    method="GET",
    headers={
        "Authorization": f'Basic {os.getenv("MAUTIC_TOKEN")}'},
    response_check=lambda response: True if response.content else False,
    log_response=True,
    xcom_push=True,
    dag=dag)

t4 = EjOperator(
    provide_context=True,
    task_id="merge_ej_mautic_analytics",
    dag=dag
)

[t1, t2, t3] >> t4

from airflow.models import DAG
from airflow.operators.http_operator import SimpleHttpOperator
import datetime

dag = DAG('osf_pipeline')

t1 = SimpleHttpOperator(
    start_date=datetime.datetime.now(),
    task_id="request_ej_reports_data",
    http_conn_id="ej_api",
    endpoint='/api/v1/conversations/1/reports?fmt=csv&&export=votes',
    method="GET",
    headers={"Accept": "text/csv"},
    response_check=lambda response: True if response.content else False,
    log_response=True,
    dag=dag)


t2 = SimpleHttpOperator(
    start_date=datetime.datetime.now(),
    task_id="request_mautic_data",
    http_conn_id="mautic_api",
    endpoint='/api/contacts/',
    method="GET",
    headers={"Authorization": "Basic cGVuY2lsbGFiczpAbTR1NzE1"},
    response_check=lambda response: True if response.content else False,
    log_response=True,
    dag=dag)
[t1, t2]

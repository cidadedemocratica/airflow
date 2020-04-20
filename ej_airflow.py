from airflow.models import DAG
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.operators.python_operator import PythonOperator
import json
import datetime

dag = DAG('osf_pipeline')


def write_to_file(data):
    with open("/tmp/airflow_data.json", "w") as f:
        f.write(json.dumps(data))


def merge_data(**context):
    ej_votes_list = json.loads(context['task_instance'].xcom_pull(
        task_ids='request_ej_reports_data'))
    mautic_data = json.loads(context['task_instance'].xcom_pull(
        task_ids='request_mautic_data'))
    mautic_contact = mautic_data["contacts"]["1"]
    merge_data = {}
    for vote in ej_votes_list:
        if(len(vote["email"].split('-')) > 1):
            mtc_id = vote["email"].split('-')[0]
            label = vote["email"].split('-')[1]
            if(mtc_id == "1" and label == 'mautic@mail.com'):
                merge_data = {**vote, **mautic_contact}
                break
        continue
    write_to_file(merge_data)
    return merge_data


t1 = SimpleHttpOperator(
    start_date=datetime.datetime.now(),
    task_id="request_ej_reports_data",
    http_conn_id="ej_api",
    endpoint='/api/v1/conversations/1/reports?fmt=json&&export=votes',
    method="GET",
    headers={"Accept": "text/csv"},
    response_check=lambda response: True if response.content else False,
    log_response=True,
    xcom_push=True,
    dag=dag)


t2 = SimpleHttpOperator(
    start_date=datetime.datetime.now(),
    task_id="request_mautic_data",
    http_conn_id="mautic_api",
    endpoint='/api/contacts/',
    method="GET",
    headers={"Authorization": "Basic ZGF2aWRjYXJsb3M6RGF2aWRAMTNjYQ=="},
    response_check=lambda response: True if response.content else False,
    log_response=True,
    xcom_push=True,
    dag=dag)

t3 = PythonOperator(
    start_date=datetime.datetime.now(),
    provide_context=True,
    python_callable=merge_data,
    task_id="merge_ej_mautic_data",
    dag=dag
)


[t1, t2] >> t3

from airflow.models import DAG
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.operators.python_operator import PythonOperator
import json
import datetime
import re

dag = DAG('osf_pipeline')


def write_to_file(data):
    with open("/tmp/airflow_data.json", "w") as f:
        f.write(json.dumps(data))


def merge_data(**context):
    list_of_ej_votes = json.loads(context['task_instance'].xcom_pull(
        task_ids='request_ej_reports_data'))
    mautic_data = json.loads(context['task_instance'].xcom_pull(
        task_ids='request_mautic_data'))
    list_of_mautic_contacts_ids = list(mautic_data["contacts"])
    merge_data = {}
    for vote in list_of_ej_votes:
        if(len(vote["email"].split('-')) > 1):
            mtc_id = vote["email"].split('-')[0]
            email_sufix = vote["email"].split('-')[1]
            if(email_sufix == 'mautic@mail.com'):
                if(mtc_id in list_of_mautic_contacts_ids):
                    _ga = mautic_data["contacts"][mtc_id]["fields"]["core"]["gid"]["value"]
                    _gaValue = re.sub(r'^GA[0-9]*\.[0-9]*\.*', '', _ga)
                    mautic_email = mautic_data["contacts"][mtc_id]["fields"]["core"]["email"]["value"]
                    first_name = mautic_data["contacts"][mtc_id]["fields"]["core"]["firstname"]["value"]
                    last_name = mautic_data["contacts"][mtc_id]["fields"]["core"]["lastname"]["value"]
                    if(_ga):
                        merge_data = {**vote, **{"analytics_client_id": _gaValue,
                                                 "mautic_email": mautic_email,
                                                 "mautic_first_name": first_name,
                                                 "mautic_last_name": last_name}}
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

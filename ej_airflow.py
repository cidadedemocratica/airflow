from airflow.models import DAG
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.operators.python_operator import PythonOperator
import json
import datetime
import re
import pandas as pd
import numpy as np
import analytics_api as analytics

dag = DAG('osf_pipeline')


def collect_client_page_view(client_ids):
    analytics_client = analytics.initialize_analyticsreporting()
    for _id in client_ids:
        response = analytics.get_report(analytics_client, _id)
        print("RESPONSE: ", response)


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
    print("MERGED DATA: ", merge_data)
    if merge_data:
        df1 = pd.DataFrame([merge_data])
        df2 = pd.read_csv('/tmp/analytics.csv',
                          dtype={'Client Id': str}, header=5)
        df2 = df2.rename(columns={'Client Id': 'analytics_client_id'})
        df3 = pd.merge(df1, df2, on='analytics_client_id')
        analytics_client = analytics.initialize_analyticsreporting()
        analytic_activities = []
        for _id in df3['analytics_client_id']:
            response = analytics.get_report(analytics_client, _id)
            for session in response['sessions']:
                for activity in session['activities']:
                    activity['analytics_client_id'] = _id
                    analytic_activities.append(activity)

        df4 = pd.DataFrame(analytic_activities)
        df3.to_csv('/tmp/ej_analytics_mautic.csv')
        df4.to_csv('/tmp/analytics_page_view.csv')


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

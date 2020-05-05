from airflow.models import DAG
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.operators.python_operator import PythonOperator
import json
import datetime
import re
import pandas as pd
import analytics_api as analytics
from dateutil.parser import *

dag = DAG('osf_pipeline')

ENV = "prod"
CONFIG = {
    "local": {
        "conversation_id": "1",
        "mautic_token": "cGVuY2lsbGFiczpAbTR1NzE1"
    },
    "prod": {
        "conversation_id": "56",
        "mautic_token": "cmljYXJkb0BjaWRhZGVkZW1vY3JhdGljYS5vcmcuYnI6cVlVNjQzNHJPRjNQ"
    }
}


def vote_belongs_to_activity(voteCreatedTime, activityTime):
    utc_vote_date = parse(voteCreatedTime)
    utc_offeset_timedelta = datetime.datetime.utcnow() - datetime.datetime.now()
    # utc_activity_time = parse(
    #    activityTime) + utc_offeset_timedelta + datetime.timedelta(hours=4)
    utc_activity_time = parse(activityTime) + utc_offeset_timedelta
    deltaDate = utc_activity_time + datetime.timedelta(minutes=5)
    print(utc_vote_date < deltaDate and utc_vote_date >= utc_activity_time)
    return utc_vote_date < deltaDate and utc_vote_date >= utc_activity_time


def merge_data(**context):
    ej_votes = json.loads(context['task_instance'].xcom_pull(
        task_ids='request_ej_reports_data'))
    mautic_data = json.loads(context['task_instance'].xcom_pull(
        task_ids='request_mautic_data'))
    list_of_mautic_contacts_ids = list(mautic_data["contacts"])
    ej_mautic_analytics = []
    for vote in ej_votes:
        if(len(vote["email"].split('-')) > 1):
            mtc_id = vote["email"].split('-')[0]
            email_sufix = vote["email"].split('-')[1]
            if(email_sufix == 'mautic@mail.com'):
                if(mtc_id in list_of_mautic_contacts_ids):
                    _ga = mautic_data["contacts"][mtc_id]["fields"]["core"]["gid"]["value"]
                    if(_ga):
                        _gaValue = re.sub(r'^GA[0-9]*\.[0-9]*\.*', '', _ga)
                        mautic_email = mautic_data["contacts"][mtc_id]["fields"]["core"]["email"]["value"]
                        first_name = mautic_data["contacts"][mtc_id]["fields"]["core"]["firstname"]["value"]
                        last_name = mautic_data["contacts"][mtc_id]["fields"]["core"]["lastname"]["value"]
                        ej_mautic_analytics.append({**vote, **{"analytics_client_id": _gaValue,
                                                               "mautic_email": mautic_email,
                                                               "mautic_first_name": first_name,
                                                               "mautic_last_name": last_name}})
    print("MERGED DATA: ", ej_mautic_analytics)
    if merge_data:
        df1 = pd.DataFrame(ej_mautic_analytics)
        analytics_user_explorer = pd.read_csv('/tmp/analytics.csv',
                                              dtype={'Client ID': str}, header=5)
        df2 = analytics_user_explorer.rename(
            columns={'Client ID': 'analytics_client_id'})
        df3 = pd.merge(df1, df2, on='analytics_client_id')
        analytics_client = analytics.initialize_analyticsreporting()
        analytic_activities = []
        for _id in df3['analytics_client_id']:
            response = analytics.get_report(analytics_client, _id)
            for session in response['sessions']:
                for activity in session['activities']:
                    for voteCreatedTime in df3[df3['analytics_client_id'] == _id]['criado']:
                        belongs = vote_belongs_to_activity(
                            voteCreatedTime, activity['activityTime'])
                        if(belongs):
                            df3.loc[df3['analytics_client_id'] == _id,
                                    'analytics_source'] = activity['source']
                            df3.loc[df3['analytics_client_id'] ==
                                    _id, 'analytics_medium'] = activity['medium']
                            df3.loc[df3['analytics_client_id'] ==
                                    _id, 'pageview'] = activity['pageview']['pagePath']
                            df3.to_csv('/tmp/ej_analytics_mautic.csv')


t1 = SimpleHttpOperator(
    start_date=datetime.datetime.now(),
    task_id="request_ej_reports_data",
    http_conn_id="ej_prod_api",
    endpoint=f'/api/v1/conversations/{CONFIG[ENV]["conversation_id"]}/reports?fmt=json&&export=votes',
    method="GET",
    headers={"Accept": "text/csv"},
    response_check=lambda response: True if response.content else False,
    log_response=True,
    xcom_push=True,
    dag=dag)


t2 = SimpleHttpOperator(
    start_date=datetime.datetime.now(),
    task_id="request_mautic_data",
    http_conn_id="mautic_prod_api",
    endpoint='/api/contacts?search=gid:GA',
    method="GET",
    headers={
        "Authorization": f'Basic {CONFIG[ENV]["mautic_token"]}'},
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

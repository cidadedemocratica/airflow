import os
from airflow.models import DAG
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.operators.python_operator import PythonOperator
from dateutil.parser import *
import json
import datetime
import re
import pandas as pd
import analytics_api as analytics

from dotenv import load_dotenv
load_dotenv()


dag = DAG('osf_pipeline')


def vote_belongs_to_activity(voteCreatedTime, activityTime):
    utc_vote_date = parse(voteCreatedTime)
    utc_offeset_timedelta = datetime.datetime.utcnow() - datetime.datetime.now()
    # utc_activity_time = parse(
    #    activityTime) + utc_offeset_timedelta + datetime.timedelta(hours=4)
    utc_activity_time = parse(activityTime) + utc_offeset_timedelta
    deltaDate = utc_activity_time + datetime.timedelta(minutes=5)
    print(utc_vote_date < deltaDate and utc_vote_date >= utc_activity_time)
    return utc_vote_date < deltaDate and utc_vote_date >= utc_activity_time


def get_ej_votes_from_xcom(context):
    return json.loads(context['task_instance'].xcom_pull(
        task_ids='request_ej_reports_data'))


def get_mautic_contacts_from_xcom(context):
    return json.loads(context['task_instance'].xcom_pull(
        task_ids='request_mautic_data'))["contacts"]


def get_mtc_id_from_email(email):
    return email.split('-')[0]


def get_email_sufix(email):
    return email.split('-')[1]


def voter_is_a_mautic_contact(vote):
    if(len(vote["email"].split('-')) > 1):
        mtc_id = get_mtc_id_from_email(vote["email"])
        email_sufix = get_email_sufix(vote["email"])
        if(email_sufix == 'mautic@mail.com'):
            return True
    return False


def get_analytics_ga(contacts, mtc_id):
    return contacts[mtc_id]["fields"]["core"]["gid"]["value"]


def parse_ga(_ga):
    return re.sub(r'^GA[0-9]*\.[0-9]*\.*', '', _ga)


def merge_vote_mautic_analytics(contact, vote, _ga):
    _gaValue = parse_ga(_ga)
    mautic_email = contact["fields"]["core"]["email"]["value"]
    first_name = contact["fields"]["core"]["firstname"]["value"]
    last_name = contact["fields"]["core"]["lastname"]["value"]
    return {**vote, **{"analytics_client_id": _gaValue,
                       "mautic_email": mautic_email,
                       "mautic_first_name": first_name,
                       "mautic_last_name": last_name}}


def get_analytics_activities(ej_mautic_analytics):
    if merge_data:
        df1 = pd.DataFrame(ej_mautic_analytics)
        analytics_user_explorer = pd.read_csv('/tmp/analytics.csv',
                                              dtype={'Client ID': str}, header=5)
        df2 = analytics_user_explorer.rename(
            columns={'Client ID': 'analytics_client_id'})
        df3 = pd.merge(df1, df2, on='analytics_client_id')
        analytics_client = analytics.initialize_analyticsreporting()
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


def merge_data(**context):
    ej_votes = get_ej_votes_from_xcom(context)
    mautic_contacts = get_mautic_contacts_from_xcom(context)
    list_of_mautic_contacts_ids = list(mautic_contacts)
    ej_mautic_analytics = []
    for vote in ej_votes:
        if(voter_is_a_mautic_contact(vote)):
            mtc_id = get_mtc_id_from_email(vote["email"])
            if(mtc_id in list_of_mautic_contacts_ids):
                _ga = get_analytics_ga(mautic_contacts, mtc_id)
                if(_ga):
                    compiled_data = merge_vote_mautic_analytics(
                        mautic_contacts[mtc_id], vote, _ga)
                    ej_mautic_analytics.append(compiled_data)

    print("MERGED DATA: ", ej_mautic_analytics)
    get_analytics_activities(ej_mautic_analytics)


t1 = SimpleHttpOperator(
    start_date=datetime.datetime.now(),
    task_id="request_ej_reports_data",
    http_conn_id=os.getenv("ej_conn_id"),
    endpoint=f'/api/v1/conversations/{os.getenv("CONVERSATION_ID")}/reports?fmt=json&&export=votes',
    method="GET",
    headers={"Accept": "text/csv"},
    response_check=lambda response: True if response.content else False,
    log_response=True,
    xcom_push=True,
    dag=dag)


t2 = SimpleHttpOperator(
    start_date=datetime.datetime.now(),
    task_id="request_mautic_data",
    http_conn_id=os.getenv("mautic_conn_id"),
    endpoint='/api/contacts?search=gid:GA',
    method="GET",
    headers={
        "Authorization": f'Basic {os.getenv("MAUTIC_TOKEN")}'},
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

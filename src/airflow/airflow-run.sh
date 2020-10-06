#!/bin/bash
rm -rf /var/airflow/airflow.cfg
ln -s /home/airflow/dags/src/airflow/airflow.cfg /var/airflow/
cp /home/airflow/dags/src/.analyticsreporting.dat /var/airflow
cp /home/airflow/dags/src/.analyticsreporting.dat /tmp
cp /home/airflow/dags/src/airflow/client_secrets.json /tmp/
cp /home/airflow/dags/src/airflow/.*.env /tmp/
rm /var/airflow/airflow-webserver.pid

#TODO: only initdb if db does not exists
#python /home/airflow/dags/src/airflow/create_superuser.py
#airflow initdb

python /home/airflow/dags/src/dashboard/server.py &
airflow webserver -p 8080 & 
airflow scheduler

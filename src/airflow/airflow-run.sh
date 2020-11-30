#!/bin/bash
rm -rf /var/airflow/airflow.cfg
ln -s /home/airflow/dags/src/airflow/airflow.cfg /var/airflow/
cp /home/airflow/dags/src/.analyticsreporting.dat /var/airflow
cp /home/airflow/dags/src/.analyticsreporting.dat /tmp
cp /home/airflow/dags/src/airflow/client_secrets.json /tmp/
cp /home/airflow/dags/src/airflow/.*.env /tmp/
rm /var/airflow/airflow-webserver.pid
airflow initdb 2> /dev/null
python /home/airflow/dags/src/airflow/create_superuser.py 2> /dev/null
airflow webserver -p 8080 & 
airflow scheduler

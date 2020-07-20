#!/bin/bash
rm -rf /var/airflow/airflow.cfg
ln -s /home/airflow/dags/src/airflow/airflow.cfg /var/airflow/
python /home/airflow/dags/src/dashboard/server.py &
airflow initdb
airflow webserver -p 8080 & 
airflow scheduler


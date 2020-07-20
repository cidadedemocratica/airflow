#!/bin/bash
rm -rf /home/airflow/airflow.cfg
ln -s /home/airflow/dags/src/airflow/airflow.cfg /home/airflow/
python /home/airflow/dags/src/dashboard/server.py &
airflow webserver -p 8080 & 
airflow scheduler


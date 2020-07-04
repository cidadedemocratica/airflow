#!/bin/bash
rm -rf /home/airflow/airflow.cfg
ln -s /home/airflow/dags/src/airflow/airflow.cfg /home/airflow/
airflow webserver -p 8080 & 
airflow scheduler


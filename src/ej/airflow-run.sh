#!/bin/bash
ln -s /home/airflow/dags/src/airflow.cfg /home/airflow/
airflow webserver -p 8080 & 
airflow scheduler


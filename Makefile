up:
	docker-compose up

stop:
	docker-compose stop

build:
	docker-compose build --no-cache

init:
	mkdir -p ./src/logs ./src/plugins
	echo -e "AIRFLOW_UID=$$(id -u)\nAIRFLOW_GID=0" > .env
	docker-compose up airflow-init
	docker-compose up

create-connections:
	docker exec -t airflow_dags_airflow-webserver_1 /bin/bash -c "python dags/create_connections.py"

stop:
	docker-compose stop

rm: stop
	docker-compose rm

attach:
	docker exec -it airflow_dags_airflow-webserver_1 bash

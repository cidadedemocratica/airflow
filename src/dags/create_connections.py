from airflow.models.connection import Connection
from airflow import settings

ej_api_connection = Connection(
    conn_id="ej_dev_api",
    conn_type="http",
    description="ejplatform api connection",
    host="192.168.15.101:8000",
    schema="http",
    login="",
    password="",
    extra="",
)

mautic_api_connection = Connection(
    conn_id="mautic_dev_api",
    conn_type="http",
    description="mautic api connection",
    host="contatos.ejparticipe.org",
    schema="https",
    login="",
    password="",
    extra="",
)
session = settings.Session()
if len(session.query(Connection).filter_by(conn_id="ej_dev_api").all()) == 0:
    session.add(ej_api_connection)

if len(session.query(Connection).filter_by(conn_id="mautic_dev_api").all()) == 0:
    session.add(mautic_api_connection)

session.commit()
session.close()

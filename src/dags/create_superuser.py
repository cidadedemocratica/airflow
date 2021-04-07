import airflow
from airflow import models, settings
from airflow.contrib.auth.backends.password_auth import PasswordUser
user = PasswordUser(models.User())
user.username = 'pencillabs'
user.email = 'contato@pencillabs.com.br'
user.password = 'pencil@labs'
user.superuser = True
session = settings.Session()
session.add(user)
session.commit()
session.close()

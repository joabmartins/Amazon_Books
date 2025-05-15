# PASSO 1

# LIBS A SEREM IMPORTADAS
from airflow import DAG # lib para criar DAGs no airflow
from datetime import datetime, timedelta # lib para poder definir data/hora nos parâmetros da DAG 
# from datetime import datetime, timedelta (erra de propósito para mostrar como debugar lá no server)

# PARAMETROS
# Parâmetros da DAG
default_args = {
     'owner': 'airflow',
     'depends_on_past': False,
     'start_date': datetime(2025, 5, 8), # data de hoje
     'retries': 1,
     'retry_delay': timedelta(minutes=5),
     'schedule_interval': '@daily'
}

# DAGS
dag = DAG(
     'books_main',
     default_args=default_args,
     description='A simple DAG to fetch book data from Amazon and store it in Postgres',
)
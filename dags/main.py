
# LIBS A SEREM IMPORTADAS
# -> 01
from airflow import DAG # lib para criar DAGs no airflow
from datetime import datetime, timedelta # lib para poder definir/formatar data/hora nos parâmetros da DAG 
# from datetime import datetime, timedelta (erra de propósito para mostrar como debugar lá no server)
# -> 06 (Executar a pipeline)
from airflow.operators.python import PythonOperator
# -> 09
import requests
import pandas as pd
from bs4 import BeautifulSoup
# -> 13
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
# -> 16
from airflow.providers.postgres.hooks.postgres import PostgresHook

# PARAMETROS
# Parâmetros da DAG
# -> 02
default_args = {
     'owner': 'airflow',
     'depends_on_past': False,
     'start_date': datetime(2025, 5, 8), # data de hoje
     'retries': 1,
     'retry_delay': timedelta(minutes=5),
     'schedule_interval': '@daily'
}

# -> 07
headers = {
    "Referer": 'https://www.amazon.com/',
    "Sec-Ch-Ua": '"Not(A:Brand";v="99", "Opera GX";v="118", "Chromium";v="133"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "Windows",
     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 OPR/118.0.0.0',
}


# DAGS
# -> 03 (Observa no servidor)
dag = DAG(
     'books_main',
     default_args=default_args,
     description='A simple DAG to fetch book data from Amazon and store it in Postgres',
)

# TASKS
# -> 04 
def iniciar_pipeline(ti):
     print("Hello, World!")

# -> 08
def get_books(num_books, ti):
     base_url = f"https://lista.mercadolivre.com.br/data-engineering-books"

     books = []
     seen_titles = set()  # To keep track of seen titles

     first_item_page = 1

     while len(books) < num_books:
          url = f"{base_url}_Desde_{first_item_page}_NoIndex_True"
          
          # Send a request to the URL
          response = requests.get(url, headers=headers)
          print("resposta...............")
          print(response.status_code)
          print(response)
          print(".......................") # (testar lá no server pra ver se tá funcionando)
          if response.status_code == 200:
               # Parse the content of the request with BeautifulSoup
               soup = BeautifulSoup(response.content, "html.parser")
               #print(soup)
               #book_containers = soup.find_all("div", {"role": "listitem"})
               book_containers = soup.find_all("li", {"class": "ui-search-layout__item"})
               #print(book_containers)
               for book in book_containers:
                    #price = book.find("span", {"class": "a-offscreen"})
                    title = book.find("a", {"class": "poly-component__title"})
                    price = book.find("span", {"class": "andes-money-amount__fraction"})
                    #print(rating)
                    if title and price:
                         book_title = title.text.strip()
                         if book_title not in seen_titles:
                              seen_titles.add(book_title)
                              books.append({
                                   "Title": book_title,
                                   "Price": price.text.strip()
                              })

                    #print(book_rating)
               first_item_page += 50
          else:
               print("status_code...............................")
               print(response.status_code)
               print("text...............................")
               print(response.text)
               break

     size = len(books)
     print("tamanho array")
     print(size)

     books = books[:num_books]

     df = pd.DataFrame(books)

     df.drop_duplicates(subset="Title", inplace=True)

     ti.xcom_push(key='book_data', value=df.to_dict('records'))

# -> 15
def insert_book_data_into_postgres(ti):
     book_data = ti.xcom_pull(key='book_data', task_ids='fetch_book_data')
     if not book_data:
          raise ValueError("No book data found")
     
     postgres_hook = PostgresHook(postgres_conn_id='books_connection')
     insert_query = """
     INSERT INTO books_ml (title, price)
     VALUES (%s, %s)
     """
     for book in book_data:
          postgres_hook.run(insert_query, parameters=(book['Title'], book['Price']))

# OPERATORS
# -> 05
init_task = PythonOperator(
     task_id='init',
     python_callable=iniciar_pipeline,
     dag=dag,
)

# -> 10
fetch_book_data_task = PythonOperator(
    task_id='fetch_book_data',
    python_callable=get_books,
    op_args=[100],  # Number of books to fetch
    dag=dag,
)

# -> 12
create_table_task = SQLExecuteQueryOperator(
     task_id='create_table',
     conn_id='books_connection',
     sql="""
     CREATE TABLE IF NOT EXISTS books_ml (
          id SERIAL PRIMARY KEY,
          title TEXT NOT NULL,
          price TEXT)
     """,
     dag=dag,
)

# -> 17
insert_book_data_task = PythonOperator(
    task_id='insert_book_data',
    python_callable=insert_book_data_into_postgres,
    dag=dag,
)

# -> 11 (executa no servidor)
# init_task >> fetch_book_data_task 
# -> 14 (executa no servidor)
# init_task >> fetch_book_data_task >> create_table_task
# -> 18 (executa no servidor e olha o número de linhas salvas no banco)
init_task >> fetch_book_data_task >> create_table_task >> insert_book_data_task
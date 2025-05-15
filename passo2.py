from datetime import datetime, timedelta
from airflow import DAG
import requests
from bs4 import BeautifulSoup
from airflow.operators.python import PythonOperator

default_args = {
     'owner': 'airflow',
     'depends_on_past': False,
     'start_date': datetime(2025, 5, 8),
     'retries': 1,
     'retry_delay': timedelta(minutes=5),
     'schedule_interval': '@daily'
}

dag = DAG(
     'connection_test',
     default_args=default_args,
     description='A simple DAG to fetch book data from Amazon and store it in Postgres',
)


headers = {
    "Referer": 'https://www.amazon.com/',
    "Sec-Ch-Ua": '"Not(A:Brand";v="99", "Opera GX";v="118", "Chromium";v="133"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "Windows",
    #'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 OPR/118.0.0.0'
     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 OPR/118.0.0.0',
}

def get_amazon_data_books(num_books, ti):
# Base URL of the Amazon search results for data science books
     #base_url = f"https://www.amazon.com/s?k=data+engineering+books"
     base_url = f"https://lista.mercadolivre.com.br/data-engineering-books"

     books = []
     seen_titles = set()  # To keep track of seen titles

     first_item_page = 1

     print("números livros")
     print(num_books)

     while len(books) < num_books:
          url = f"{base_url}_Desde_{first_item_page}_NoIndex_True"
          
          # Send a request to the URL
          response = requests.get(url, headers=headers)
          print("resposta...............")
          print(response.status_code)
          print(response)
          print(".......................")
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

     
 

def next_task(ti):
     print("Ok")

fetch_book_data_task = PythonOperator(
    task_id='fetch_book_data',
    python_callable=get_amazon_data_books,
    op_args=[100],  # Number of books to fetch
    dag=dag,
)

insert_book_data_task = PythonOperator(
    task_id='ok',
    python_callable=next_task,
    dag=dag,
)

#dependencies

fetch_book_data_task >> insert_book_data_task
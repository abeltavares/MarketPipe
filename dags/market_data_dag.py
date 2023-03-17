"""
These scripts set up two DAGs for collecting and storing financial market data, including stock data and cryptocurrency data.

The DAG for stock data collection and storage consists of three tasks:

get_stocks: retrieves the symbol of the top 5 stocks accordingly with market performance
get_stock_data: retrieves detailed information of the stocks retrieved in task 1
store_stock_data_in_database: stores the stock data in a database
The DAG for cryptocurrency data collection and storage consists of two tasks:

get_crypto_data: retrieves data for the top 5 cryptocurrencies accordingly with market performance
store_crypto_data_in_database: stores the cryptocurrency data in a database
Both DAGs run at 11 PM, as specified by the schedule_interval parameter. Task dependencies are established such that get_stocks (for the stock data DAG) and get_crypto_data (for the cryptocurrency data DAG) must complete before their respective downstream tasks. Similarly, get_stock_data must complete before store_stock_data for the stock data DAG.

The data_collection_storage_stocks DAG is scheduled to run everyday at 11 PM from Monday to Friday, as specified by the schedule_interval parameter. On the other hand, the data_collection_storage_crypto DAG is scheduled to run everyday at 11 PM, without any day-of-week restrictions.
Task dependencies are established such that get_stocks must complete before get_stock_data, and get_stock_data must complete before store_stock_data. Similarly, get_crypto_data must complete before store_crypto_data.

The script makes use of PythonOperator to define the tasks, and passes output of one task to the input of the next using op_kwargs and op_args parameters. The get_stocks and get_crypto_data tasks have no dependencies on any previous tasks.
"""

from airflow.operators.python import PythonOperator
from airflow.models import DAG
from datetime import datetime, timedelta
from data_collection_storage import (
    get_stocks, get_stock_data, store_stock_data, 
    get_crypto_data, store_crypto_data
)

# Define default arguments for the DAGs
default_args_stocks = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 3, 15),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
}

default_args_cryptos = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 3, 15),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
}

# Create the DAG for stock data collection and storage
dag_stocks = DAG(
    'data_collection_storage_stocks', 
    default_args=default_args_stocks, 
    schedule_interval='0 23 * * 1-5', # Schedule to run everyday at 11 PM from Monday to Friday
    description='Collect and store stock data' # Add description for the DAG
)

# Create the DAG for cryptocurrency data collection and storage
dag_cryptos = DAG(
    'data_collection_storage_crypto', 
    default_args=default_args_cryptos, 
    schedule_interval='0 23 * * *', # Schedule to run everyday at 11 PM
    description='Collect and store cryptocurrency data' # Add description for the DAG
)

# Define the tasks for stock data collection and storage
get_stocks_task = PythonOperator(
    task_id='get_stocks',
    python_callable=get_stocks,
    dag=dag_stocks,
)

get_stock_data_task = PythonOperator(
    task_id='get_stock_data',
    python_callable=get_stock_data,
    op_kwargs={'symbols': get_stocks_task.output},
    dag=dag_stocks,
)

store_stock_data_task = PythonOperator(
    task_id='store_stock_data',
    python_callable=store_stock_data,
    op_kwargs={'data': get_stock_data_task.output},
    dag=dag_stocks,
)

# Define the tasks for cryptocurrency data collection and storage
get_crypto_data_task = PythonOperator(
    task_id='get_crypto_data',
    python_callable=get_crypto_data,
    dag=dag_cryptos,
)

store_crypto_data_task = PythonOperator(
    task_id='store_crypto_data',
    python_callable=store_crypto_data,
    op_args=[get_crypto_data_task.output],
    dag=dag_cryptos,
)

"""
This script sets up a DAG for collecting and storing stock data from the financialmodelingprep and Alpha Advantage APIs.  
It consists of three tasks:
    1. get_stocks: retrieves the symbol of the top 5 stocks of the specified market performance (gainers, by default)
    2. get_stock_data: retrieves detailed information of the stocks retrieved in task 1
    3. store_stock_data_in_database: stores the stock data in a database
The tasks run every day at 7 PM, as specified by the schedule_interval parameter. Task dependencies are established
such that get_stocks must complete before get_stock_data, and get_stock_data must complete before store_stock_data_in_database.
"""
from airflow.operators.python import PythonOperator
from airflow.models import DAG
from datetime import datetime, timedelta
from data_collection_storage import get_stocks, get_stock_data, store_stock_data_in_database
  
# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 2, 4),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create a DAG instance
dag = DAG(
    'stock_data_collection', 
    default_args=default_args, 
    schedule='50 15 * * *', # Schedule to run everyday at 7 PM
    description='Collect and store stock data' # Add description for the DAG
)

# Define the first task - get_stocks
get_stocks_task = PythonOperator(
    task_id='get_stock',
    python_callable=get_stocks,
    op_args=['gainers'], # Add a descriptive comment for the op_args
    dag=dag,
)

# Define the second task - get_stock_data
get_stock_data_task = PythonOperator(
    task_id='get_data',
    python_callable=get_stock_data,
    op_args=[get_stocks_task.output], # Pass the output of the previous task as input
    dag=dag,
)

# Define the third task - store_stock_data_in_database
store_stock_data_in_database_task = PythonOperator(
    task_id='store_data',
    python_callable=store_stock_data_in_database,
    op_args=[get_stock_data_task.output], # Pass the output of the previous task as input
    dag=dag,
)
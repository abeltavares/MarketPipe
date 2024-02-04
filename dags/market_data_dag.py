import os
import sys
from airflow.operators.python import PythonOperator
from airflow.models import DAG
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Find the parent directory
parent_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(parent_dir)

# Add the project root to the Python path
sys.path.insert(0, project_root)

from core.market_data_processor import (
    StockApiClient,
    CryptoApiClient,
    Storage,
    MarketDataEngine,
)

# Define default arguments for the DAGs
default_args_stocks = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2023, 3, 15),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
}

default_args_cryptos = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2023, 3, 15),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
}

# Create instances of the classes
stock_api_client = StockApiClient(
    os.environ["ALPHA_API_KEY"], os.environ["PREP_API_KEY"]
)
crypto_api_client = CryptoApiClient(os.environ["COIN_API_KEY"])
db_connector = Storage(
    os.getenv["POSTGRES_HOST"],
    os.getenv["POSTGRES_PORT"],
    os.getenv["POSTGRES_DB"],
    os.getenv["POSTGRES_USER"],
    os.getenv["POSTGRES_PASSWORD"],
)
stock_engine = MarketDataEngine(stock_api_client, db_connector)
crypto_engine = MarketDataEngine(crypto_api_client, db_connector)

# Create the DAG for stock data collection and storage
dag_stocks = DAG(
    "data_collection_storage_stocks",
    default_args=default_args_stocks,
    schedule_interval="0 23 * * 1-5",  # Schedule to run everyday at 11 PM from Monday to Friday
    description="Collect and store stock data",
)

# Create the DAG for cryptocurrency data collection and storage
dag_cryptos = DAG(
    "data_collection_storage_crypto",
    default_args=default_args_cryptos,
    schedule_interval="0 23 * * *",  # Schedule to run everyday at 11 PM
    description="Collect and store cryptocurrency data",
)

# Define the task for stock data collection and storage
process_stock_data_task = PythonOperator(
    task_id="get_stocks",
    python_callable=stock_engine.process_stock_data,
    dag=dag_stocks,
)

# Define the tasks for cryptocurrency data collection and storage
process_crypto_data_task = PythonOperator(
    task_id="get_crypto",
    python_callable=crypto_engine.process_crypto_data,
    dag=dag_cryptos,
)

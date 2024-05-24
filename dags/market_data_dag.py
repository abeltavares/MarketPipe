from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import logging
from utils.market_data_processor_utils import read_json
from core.data_processor import DataProcessor

config = read_json("mdp_config.json")

default_args = {
    "owner": config.get("owner", "airflow"),
    "depends_on_past": False,
    "start_date": datetime.now(),
    "email_on_failure": config.get("email_on_failure", False),
    "email_on_retry": config.get("email_on_retry", False),
    "retries": config.get("retries", 1),
}


def create_market_data_dag(asset_type, dag_id, description):
    dag = DAG(
        dag_id,
        default_args=default_args,
        schedule_interval=config["assets"][asset_type]["schedule_interval"],
        description=description,
    )

    market_processor = DataProcessor(asset_type)

    with dag:
        get_data_task = PythonOperator(
            task_id=f"get_{asset_type}_data",
            python_callable=market_processor.get_data,
        )

        store_data_task = PythonOperator(
            task_id=f"store_{asset_type}_data",
            python_callable=market_processor.store_data,
        )

        get_data_task >> store_data_task

    return dag


create_market_data_dag("stocks", "process_stock_data", "Collect and store stock data")
create_market_data_dag("cryptos", "process_crypto_data", "Collect and store crypto data")

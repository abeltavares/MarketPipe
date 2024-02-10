import os
import sys
import unittest
from unittest.mock import patch
from airflow.models import DagBag
from airflow.operators.python import PythonOperator
import logging

# Set the logging level to ERROR for the Airflow logger
logging.getLogger("airflow").setLevel(logging.ERROR)

# Find the parent directory
parent_directory = os.path.dirname(os.path.abspath(__file__))

# Find the project root
project_root = os.path.dirname(parent_directory)

# Add the project root to the Python path
sys.path.insert(0, project_root)

from core.market_data_processor import StockApiClient, CryptoApiClient, Storage
from dags.market_data_dag import process_crypto_data_task, process_stock_data_task


class TestMarketDataDag(unittest.TestCase):
    """
    Unit tests for the Market Data DAGs.
    """

    def setUp(self):

        self.dagbag = DagBag(
            dag_folder=os.path.join(project_root, "dags"), include_examples=False
        )
        self.stock_dag_id = "process_stock_data"
        self.crypto_dag_id = "process_crypto_data"

    def test_dag_stocks_exists(self):
        self.assertIn(self.stock_dag_id, self.dagbag.dags)

    def test_dag_stocks_loaded(self):
        dag = self.dagbag.get_dag(self.stock_dag_id)
        self.assertDictEqual(self.dagbag.import_errors, {})
        self.assertIsNotNone(dag)
        self.assertEqual(len(dag.tasks), 1)

    def test_dag_stocks_schedule_interval(self):
        dag = self.dagbag.get_dag(self.stock_dag_id)
        self.assertEqual(dag.schedule_interval, "0 23 * * 1-5")

    @patch.object(StockApiClient, "get_stocks")
    @patch.object(StockApiClient, "get_data")
    @patch.object(Storage, "store_data")
    def test_process_stock_data_task(
        self, mock_store_data, mock_get_data, mock_get_stocks
    ):
        # Setup mock behavior
        stocks = {"gainers": ["ABC"]}

        stock_data = {
            "gainers": [
                {
                    "symbol": "ABC",
                    "volume": "123456",
                    "price": "50.25",
                    "change_percent": "2.5",
                    "market_cap": "1.2B",
                    "name": "ABC Company",
                }
            ]
        }
        mock_get_stocks.return_value = stocks
        mock_get_data.return_value = stock_data

        # Get the task
        task_id = "get_stocks"

        test = PythonOperator(
            task_id=task_id,
            python_callable=process_stock_data_task.python_callable,
        )

        test.execute(context={})

        # Check if the methods were called
        mock_get_stocks.assert_called_once()
        mock_get_data.assert_called_once()
        mock_store_data.assert_called_once()

    def test_dag_cryptos_exists(self):
        self.assertIn(self.crypto_dag_id, self.dagbag.dags)

    def test_dag_cryptos_loaded(self):
        dag = self.dagbag.get_dag(self.crypto_dag_id)
        self.assertDictEqual(self.dagbag.import_errors, {})
        self.assertIsNotNone(dag)
        self.assertEqual(len(dag.tasks), 1)

    def test_dag_cryptos_schedule_interval(self):
        dag = self.dagbag.get_dag(self.crypto_dag_id)
        self.assertEqual(dag.schedule_interval, "0 23 * * *")

    @patch.object(CryptoApiClient, "get_data")
    @patch.object(Storage, "store_data")
    def test_process_crypto_data_task(self, mock_get_crypto_data, mock_store_data):
        # Get the DAG and task
        mock_get_crypto_data.return_value = {}
        task_id = "get_crypto"

        test = PythonOperator(
            task_id=task_id,
            python_callable=process_crypto_data_task.python_callable,
        )

        test.execute(context={})

        # Check if the methods were called
        mock_get_crypto_data.assert_called_once()
        mock_store_data.assert_called_once()


if __name__ == "__main__":
    unittest.main()

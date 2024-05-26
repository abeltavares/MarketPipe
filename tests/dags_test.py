import os
import sys
import unittest
from unittest.mock import patch
from airflow.models import DagBag
import logging
from dags.market_data_dag import create_market_data_dag

from core.crypto_api_client import CryptoApiClient
from core.stock_api_client import StockApiClient
from core.storage import Storage

logging.getLogger("airflow").setLevel(logging.ERROR)

parent_directory = os.path.dirname(os.path.abspath(__file__))

project_root = os.path.dirname(parent_directory)

# Add the project root to the Python path
sys.path.insert(0, project_root)


class TestMarketDataDag(unittest.TestCase):
    """
    Unit tests for the Market Data DAGs.
    """

    def setUp(self):
        with patch(
            "utils.read_json",
            return_value={
                "owner": "airflow",
                "email_on_failure": False,
                "email_on_retry": False,
                "retries": 1,
                "assets": {
                    "stocks": {"symbols": ["BREPE"], "schedule_interval": "0 13 * * *"},
                    "cryptos": {
                        "symbols": ["BTC", "ETH"],
                        "schedule_interval": "0 13 * * *",
                    },
                }
            },
        ):
            self.dagbag = DagBag(
                dag_folder=os.path.join(project_root, "dags"), include_examples=False
            )
            self.stock_dag_id = "process_stock_data"
            self.crypto_dag_id = "process_crypto_data"

            self.stock_dag = create_market_data_dag("stocks", "process_stock_data", "Collect and store stock data")
            self.crypto_dag = create_market_data_dag("cryptos", "process_crypto_data",
                                                     "Collect and store crypto data")

    def test_dag_stocks_exists(self):
        self.assertIn(self.stock_dag_id, self.dagbag.dags)

    def test_dag_stocks_loaded(self):
        dag = self.dagbag.get_dag(self.stock_dag_id)
        self.assertDictEqual(self.dagbag.import_errors, {})
        self.assertIsNotNone(dag)
        self.assertEqual(len(dag.tasks), 2)

    def test_dag_stocks_schedule_interval(self):
        dag = self.dagbag.get_dag(self.stock_dag_id)
        self.assertEqual(dag.schedule_interval, "0 13 * * *")

    @patch.object(StockApiClient, "get_data")
    @patch.object(Storage, "store_data")
    def test_process_stock_data_task(self, mock_store_data, mock_get_data):
        get_data_task = self.stock_dag.get_task("get_stocks_data")
        store_data_task = self.stock_dag.get_task("store_stocks_data")

        get_data_task.execute(context={})
        store_data_task.execute(context={"task_instance": get_data_task.output})

        mock_get_data.assert_called_once()
        mock_store_data.assert_called_once()

    def test_dag_cryptos_exists(self):
        self.assertIn(self.crypto_dag_id, self.dagbag.dags)

    def test_dag_cryptos_loaded(self):
        dag = self.dagbag.get_dag(self.crypto_dag_id)
        self.assertDictEqual(self.dagbag.import_errors, {})
        self.assertIsNotNone(dag)
        self.assertEqual(len(dag.tasks), 2)

    def test_dag_cryptos_schedule_interval(self):
        dag = self.dagbag.get_dag(self.crypto_dag_id)
        self.assertEqual(dag.schedule_interval, "0 13 * * *")

    @patch.object(CryptoApiClient, "get_data")
    @patch.object(Storage, "store_data")
    def test_process_crypto_data_task(self, mock_get_crypto_data, mock_store_data):
        get_data_task = self.crypto_dag.get_task("get_cryptos_data")
        store_data_task = self.crypto_dag.get_task("store_cryptos_data")

        get_data_task.execute(context={})
        store_data_task.execute(context={"task_instance": get_data_task.output})

        mock_get_crypto_data.assert_called_once()
        mock_store_data.assert_called_once()


if __name__ == "__main__":
    unittest.main()

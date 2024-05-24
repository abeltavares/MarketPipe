import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import logging
from utils import market_data_processor_utils
from core.market_data_processor import (
    StockApiClient,
    CryptoApiClient,
    Storage,
    MarketDataEngine,
)

class TestStorage(unittest.TestCase):
    """
    Unit tests for the Storage class.
    """

    def setUp(self):
        self.logger = MagicMock(spec=logging.Logger)

        self.storage = Storage(logger=self.logger)

    @patch.dict(
        "core.market_data_processor.os.environ",
        {
            "POSTGRES_USER": "user",
            "POSTGRES_PASSWORD": "password",
            "POSTGRES_DB": "test_db",
            "POSTGRES_HOST": "localhost",
            "POSTGRES_PORT": "5432",
        },
        clear=True,
    )
    @patch("core.market_data_processor.psycopg2.connect")
    def test_connect(self, mock_connect):
        self.storage._connect()

        mock_connect.assert_called_once_with(
            host="localhost",
            port="5432",
            database="test_db",
            user="user",
            password="password",
        )

    @patch("core.market_data_processor.psycopg2.connect")
    def test_close(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur

        self.storage._connect()
        self.storage._close()

        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("core.market_data_processor.psycopg2.connect")
    def test_store_data_with_valid_data(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_execute = mock_cur.execute
        mock_commit = mock_conn.commit

        # Test case with valid data
        data = {
            "ABC": {
                "volume": 123456,
                "price": 50.25,
                "change_percent": 2.5,
                "market_cap": "1.2B",
                "name": "ABC Company",
            }
        }
        table = "stocks"

        self.storage.store_data(data, table)

        # Assert that execute and commit methods were called
        mock_execute.assert_called_once()
        mock_execute.assert_called_once_with(
            "INSERT INTO stocks (symbol, name, market_cap, volume, price, change_percent) VALUES (%s, %s, %s, %s, %s, %s)",
            ("ABC", "ABC Company", "1.2B", 123456, 50.25, 2.5),
        )
        mock_commit.assert_called_once()

    @patch("core.market_data_processor.psycopg2.connect")
    def test_store_data_with_invalid_data_empty_symbol(self, mock_connect):
        # (empty name)
        data_invalid = {
            "ABC": {
                "volume": 1000,
                "price": 10.0,
                "change_percent": 5.0,
                "market_cap": 1000000,
                "name": "",
            }
        }

        table = "stocks"

        # Mock the logger.error method to capture log messages
        with patch.object(self.logger, "error"):
            with self.assertRaises(ValueError):
                self.storage.store_data(data_invalid, table)

    @patch("core.market_data_processor.psycopg2.connect")
    def test_store_data_with_invalid_data_type(self, mock_connect):
        data = {
            "ABC": {
                "volume": 1000,
                "price": 10.0,
                "change_percent": 5.0,
                "market_cap": 1000000,
                "name": "",
            }
        }

        table_invalid = 123  # Invalid table(not a string)

        with patch.object(self.logger, "error"):
            with self.assertRaises(TypeError):
                self.storage.store_data(data, table_invalid)


class TestMarketDataEngine(unittest.TestCase):
    """
    Unit tests for the MarketDataEngine class.
    """

    def setUp(self):
        self.stock_api_client = MagicMock(spec=StockApiClient)
        self.crypto_api_client = MagicMock(spec=CryptoApiClient)
        self.db_connector = MagicMock(spec=Storage)
        self.logger = MagicMock(spec=logging.Logger)
        self.stock_engine = MarketDataEngine(
            self.stock_api_client, self.db_connector, self.logger
        )
        self.crypto_engine = MarketDataEngine(
            self.crypto_api_client, self.db_connector, self.logger
        )

    def test_process_stock_data(self):
        self.stock_api_client.get_data.return_value = {
            "AAPL": {"price": 150.0},
            "GOOG": {"price": 2000.0},
            "MSFT": {"price": 300.0},
        }

        self.stock_engine.process_stock_data()

        self.db_connector.store_data.assert_called_once_with(
            {
                "AAPL": {"price": 150.0},
                "GOOG": {"price": 2000.0},
                "MSFT": {"price": 300.0},
            },
            "stocks",
        )

    def test_process_crypto_data(self):
        self.crypto_api_client.get_data.return_value = {
            "BTC": {"price": 50000.0},
            "ETH": {"price": 4000.0},
        }

        self.crypto_engine.process_crypto_data()

        self.crypto_api_client.get_data.assert_called_once()
        self.db_connector.store_data.assert_called_once_with(
            {"BTC": {"price": 50000.0}, "ETH": {"price": 4000.0}}, "cryptos"
        )


if __name__ == "__main__":
    unittest.main()

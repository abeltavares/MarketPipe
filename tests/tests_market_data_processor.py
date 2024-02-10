import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import logging

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


class TestStockApiClient(unittest.TestCase):
    """
    Unit tests for the StockApiClient class.
    """

    def setUp(self):
        # Mock logger for testing
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler())
        self.stock_api_client = StockApiClient(
            "alpha_api_key", "prep_api_key", logger=self.logger
        )

    def test_init(self):
        self.assertEqual(self.stock_api_client.ALPHA_API_KEY, "alpha_api_key")
        self.assertEqual(self.stock_api_client.PREP_API_KEY, "prep_api_key")

    @patch("requests.get")
    def test_get_stocks(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"symbol": "ABC"},
            {"symbol": "DEF"},
            {"symbol": "GHI"},
            {"symbol": "JKL"},
            {"symbol": "MNO"},
        ]
        mock_get.return_value = mock_response

        stocks = self.stock_api_client.get_stocks()

        self.assertEqual(
            stocks,
            {
                "gainers": ["ABC", "DEF", "GHI", "JKL", "MNO"],
                "losers": ["ABC", "DEF", "GHI", "JKL", "MNO"],
                "actives": ["ABC", "DEF", "GHI", "JKL", "MNO"],
            },
        )

    @patch("requests.get")
    def test_get_stocks_empty_data(self, mock_get):
        # Mock the response from the API with empty data
        mock_get.return_value.json.return_value = []

        # Mock the logger.error method to capture log messages
        with patch.object(self.logger, "error"):
            # Call the method under test and assert that it raises the expected exception
            with self.assertRaises(ValueError):
                self.stock_api_client.get_stocks()

    @patch("requests.get")
    def test_get_stocks_data_error(self, mock_get):
        # Mock the response from the API with invalid data
        mock_get.return_value.json.return_value = [{"invalid": "data"}]

        # Mock the logger.error method to capture log messages
        with patch.object(self.logger, "error"):
            # Call the method under test and assert that it raises the expected exception
            with self.assertRaises(KeyError):
                self.stock_api_client.get_stocks()

    @patch("requests.get")
    def test_get_data(self, mock_get):
        # Mock the response for a successful Alpha Vantage API request
        alpha_response = MagicMock()
        alpha_response.status_code = 200
        alpha_response.json.return_value = {
            "Global Quote": {
                "06. volume": "1000",
                "05. price": "150.0",
                "10. change percent": "5.0",
            }
        }

        # Mock the response for a successful Financial Modeling Prep API request
        prep_response = MagicMock()
        prep_response.status_code = 200
        prep_response.json.return_value = [
            {"companyName": "Apple Inc.", "mktCap": "2000000"}
        ]

        mock_get.side_effect = [alpha_response, prep_response]

        # Call the method under test
        symbols = {"gainers": ["AAPL"]}
        stock_data = self.stock_api_client.get_data(symbols)

        # Assertions based on the mock data
        expected_stock_data = {
            "gainers": [
                {
                    "symbol": "AAPL",
                    "volume": "1000",
                    "price": "150.0",
                    "change_percent": "5.0",
                    "market_cap": "2000000",
                    "name": "Apple Inc.",
                }
            ]
        }

        self.assertEqual(stock_data, expected_stock_data)

    @patch("requests.get")
    def test_get_alpha_data_invalid_data(self, mock_get):
        # Define symbols to be used in the test
        symbols = {"gainers": ["AAPL"]}

        # Mock the response for a successful Alpha Vantage API request
        alpha_response = MagicMock()
        alpha_response.status_code = 200
        alpha_response.json.return_value = {
            "Quote": {
                "06. volume": "1000",
                "05. price": "150.0",
                "10. change percent": "5.0",
            }
        }

        # Mock the response for a successful Financial Modeling Prep API request
        prep_response = MagicMock()
        prep_response.status_code = 200
        prep_response.json.return_value = [
            {"companyName": "Apple Inc.", "mktCap": "2000000"}
        ]

        mock_get.side_effect = [alpha_response, prep_response]

        # Mock the logger.error method to capture log messages
        with patch.object(self.logger, "error"):
            # Call the method under test and assert that it raises the expected exception
            with self.assertRaises(KeyError):
                self.stock_api_client.get_data(symbols)

    @patch("requests.get")
    def test_get_prep_data_invalid_data(self, mock_get):
        # Define symbols to be used in the test
        symbols = {"gainers": ["AAPL"]}

        # Mock the response for a successful Alpha Vantage API request
        alpha_response = MagicMock()
        alpha_response.status_code = 200
        alpha_response.json.return_value = {
            "Global Quote": {
                "06. volume": "1000",
                "05. price": "150.0",
                "10. change percent": "5.0",
            }
        }

        # Mock the response for a successful Financial Modeling Prep API request
        prep_response = MagicMock()
        prep_response.status_code = 200
        prep_response.json.return_value = [{"company": "Name"}]

        mock_get.side_effect = [alpha_response, prep_response]

        # Mock the logger.error method to capture log messages
        with patch.object(self.logger, "error"):
            # Call the method under test and assert that it raises the expected exception
            with self.assertRaises(KeyError):
                self.stock_api_client.get_data(symbols)


class TestCryptoApiClient(unittest.TestCase):
    """
    Unit tests for the CryptoApiClient class.
    """

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler())
        self.crypto_api_client = CryptoApiClient("coin_api_key", logger=self.logger)

    @patch("requests.get")
    def test_get_data(self, mock_get):
        # Mock the response from the API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "name": "BREPE",
                    "symbol": "BREPE",
                    "quote": {
                        "USD": {
                            "price": 7,
                            "volume_24h": 10,
                            "percent_change_24h": 16,
                            "market_cap": 0,
                        }
                    },
                }
            ]
        }
        mock_get.return_value = mock_response

        # Call the method under test
        data = self.crypto_api_client.get_data()

        # Assert that the method returned the expected data
        expected_data = {
            "gainers": [
                {
                    "symbol": "BREPE",
                    "name": "BREPE",
                    "volume": 10,
                    "price": 7,
                    "change_percent": 16,
                    "market_cap": 0,
                }
            ],
            "losers": [
                {
                    "symbol": "BREPE",
                    "name": "BREPE",
                    "volume": 10,
                    "price": 7,
                    "change_percent": 16,
                    "market_cap": 0,
                }
            ],
            "actives": [
                {
                    "symbol": "BREPE",
                    "name": "BREPE",
                    "volume": 10,
                    "price": 7,
                    "change_percent": 16,
                    "market_cap": 0,
                }
            ],
        }

        self.assertEqual(data, expected_data)

    @patch("requests.get")
    def test_get_data_invalid_data(self, mock_get):
        # Mock the response from the API with invalid data (missing 'quote' key)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"name": "BREPE", "symbol": "BREPE"}]
        }
        mock_get.return_value = mock_response

        # Mock the logger.error method to capture log messages
        with patch.object(self.logger, "error"):
            # Call the method under test and assert that it raises the expected exception
            with self.assertRaises(KeyError):
                self.crypto_api_client.get_data()


class TestStorage(unittest.TestCase):
    """
    Unit tests for the Storage class.
    """

    def setUp(self):
        # Mock logger for testing
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler())

        self.storage = Storage(
            "localhost", 5432, "test_db", "user", "password", logger=self.logger
        )

    @patch("psycopg2.connect")
    def test_connect(self, mock_connect):
        # Mock the cursor and its methods
        mock_conn = mock_connect.return_value
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur

        self.storage._connect()

        mock_connect.assert_called_once_with(
            host="localhost",
            port=5432,
            database="test_db",
            user="user",
            password="password",
        )
        self.assertEqual(self.storage.conn, mock_conn)
        self.assertEqual(self.storage.cur, mock_cur)

        # Ensure the connection object supports context management
        with self.storage.conn:
            pass  # This should not raise an AttributeError

    @patch("psycopg2.connect")
    def test_close(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur

        self.storage._connect()
        self.storage._close()

        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("psycopg2.connect")
    def test_store_data_with_valid_data(self, mock_connect):
        # Mock the cursor and its methods
        mock_conn = mock_connect.return_value
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_execute = mock_cur.execute
        mock_commit = mock_conn.commit

        # Test case with valid data
        data = {
            "gainers": [
                {
                    "symbol": "ABC",
                    "name": "ABC Corp",
                    "volume": 1000,
                    "price": 10.0,
                    "market_cap": 1000000,
                    "change_percent": 5.0,
                }
            ]
        }
        data_type = "stock"

        self.storage.store_data(data, data_type)

        # Assert that execute and commit methods were called
        mock_execute.assert_called_once()
        mock_execute.assert_called_once_with(
            "INSERT INTO stock_data.gainers (symbol, name, market_cap, volume, price, change_percent) VALUES (%s, %s, %s, %s, %s, %s)",
            ("ABC", "ABC Corp", 1000000, 1000, 10.0, 5.0),
        )
        mock_commit.assert_called_once()

    @patch("psycopg2.connect")
    def test_store_data_with_invalid_data_empty_symbol(self, mock_connect):
        # Test case with invalid data (empty symbol)
        data_invalid = {
            "gainers": [
                {
                    "symbol": "",
                    "name": "ABC Corp",
                    "volume": 1000,
                    "price": 10.0,
                    "market_cap": 1000000,
                    "change_percent": 5.0,
                }
            ]
        }
        data_type = "stock"

        # Mock the logger.error method to capture log messages
        with patch.object(self.logger, "error"):
            with self.assertRaises(ValueError):
                self.storage.store_data(data_invalid, data_type)

    @patch("psycopg2.connect")
    def test_store_data_with_invalid_data_type(self, mock_connect):
        # Test case with invalid data type
        data = {
            "gainers": [
                {
                    "symbol": "ABC",
                    "name": "ABC Corp",
                    "volume": 1000,
                    "price": 10.0,
                    "market_cap": 1000000,
                    "change_percent": 5.0,
                }
            ]
        }
        data_type_invalid = 123  # Invalid data type (not a string)

        # Mock the logger.error method to capture log messages
        with patch.object(self.logger, "error"):
            with self.assertRaises(TypeError):
                self.storage.store_data(data, data_type_invalid)


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
        # Mock the return values for the api_client methods
        self.stock_api_client.get_stocks.return_value = ["AAPL", "GOOG", "MSFT"]
        self.stock_api_client.get_data.return_value = {
            "AAPL": {"price": 150.0},
            "GOOG": {"price": 2000.0},
            "MSFT": {"price": 300.0},
        }

        # Call the method under test
        self.stock_engine.process_stock_data()

        # Assert that the methods were called with the expected arguments
        self.stock_api_client.get_stocks.assert_called_once()
        self.stock_api_client.get_data.assert_called_once_with(["AAPL", "GOOG", "MSFT"])
        self.db_connector.store_data.assert_called_once_with(
            {
                "AAPL": {"price": 150.0},
                "GOOG": {"price": 2000.0},
                "MSFT": {"price": 300.0},
            },
            "stock",
        )

    def test_process_crypto_data(self):
        # Mock the return value for the api_client.get_data method
        self.crypto_api_client.get_data.return_value = {
            "BTC": {"price": 50000.0},
            "ETH": {"price": 4000.0},
        }

        # Call the method under test
        self.crypto_engine.process_crypto_data()

        # Assert that the methods were called with the expected arguments
        self.crypto_api_client.get_data.assert_called_once()
        self.db_connector.store_data.assert_called_once_with(
            {"BTC": {"price": 50000.0}, "ETH": {"price": 4000.0}}, "crypto"
        )


if __name__ == "__main__":
    unittest.main()

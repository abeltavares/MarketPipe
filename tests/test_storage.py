import unittest
from unittest.mock import patch, MagicMock
import logging
from core.storage import Storage, SCHEMA_NAME


class TestStorage(unittest.TestCase):
    """
    Unit tests for the Storage class.
    """

    def setUp(self):
        self.logger = MagicMock(spec=logging.Logger)

        self.storage = Storage(logger=self.logger)

    @patch.dict(
        "core.storage.os.environ",
        {
            "POSTGRES_USER": "user",
            "POSTGRES_PASSWORD": "password",
            "POSTGRES_DB": "test_db",
            "POSTGRES_PORT": "5432",
            "POSTGRES_HOST": "postgres-source",
        },
        clear=True,
    )
    @patch("core.storage.psycopg2.connect")
    def test_connect(self, mock_connect):
        self.storage._connect()

        mock_connect.assert_called_once_with(
            host="postgres-source",
            port="5432",
            database="test_db",
            user="user",
            password="password",
        )

    @patch("core.storage.psycopg2.connect")
    def test_close(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur

        self.storage._connect()
        self.storage._close()

        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("core.storage.psycopg2.connect")
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
            f"INSERT INTO {SCHEMA_NAME}.stocks (symbol, name, market_cap, volume, price, change_percent) VALUES (%s, %s, %s, %s, %s, %s)",
            ("ABC", "ABC Company", "1.2B", 123456, 50.25, 2.5),
        )
        mock_commit.assert_called_once()

    @patch("core.storage.psycopg2.connect")
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

    @patch("core.storage.psycopg2.connect")
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

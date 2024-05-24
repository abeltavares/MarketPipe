import unittest
from unittest.mock import patch, MagicMock
import logging
from utils import market_data_processor_utils
from core.crypto_api_client import CryptoApiClient


class TestCryptoApiClient(unittest.TestCase):
    """
    Unit tests for the CryptoApiClient class.
    """

    def setUp(self):
        self.logger = MagicMock(spec=logging.Logger)
        with patch(
            "core.crypto_api_client.read_json",
            return_value={"assets": {"cryptos": {"symbols": ["BREPE"]}}},
        ):
            self.crypto_api_client = CryptoApiClient(logger=self.logger)

    @patch("core.crypto_api_client.requests.get")
    def test_get_data(
        self,
        mock_get,
    ):
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
            "BREPE": {
                "price": 7,
                "volume": 10,
                "change_percent": 16,
                "market_cap": 0,
                "name": "BREPE",
            }
        }
        self.assertEqual(data, expected_data)

    @patch("core.crypto_api_client.requests.get")
    def test_get_data_invalid_data(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"name": "BREPE", "quote": {}}]  # Simulate missing quote data
        }
        mock_get.return_value = mock_response

        with patch.object(self.logger, "error"):
            with self.assertRaises(KeyError):
                self.crypto_api_client.get_data()

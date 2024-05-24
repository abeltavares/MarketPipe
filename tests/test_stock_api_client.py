import unittest
from unittest.mock import patch, MagicMock
import logging
from core.stock_api_client import StockApiClient


class TestStockApiClient(unittest.TestCase):
    """
    Unit tests for the StockApiClient class.
    """

    def setUp(self):
        self.logger = MagicMock(spec=logging.Logger)
        with patch(
            "core.stock_api_client.read_json",
            return_value={"assets": {"stocks": {"symbols": ["AAPL"]}}},
        ):
            self.stock_api_client = StockApiClient(logger=self.logger)

    @patch("core.stock_api_client.requests.get")
    def test_get_data(self, mock_get):
        alpha_response = MagicMock()
        alpha_response.status_code = 200
        alpha_response.json.return_value = {
            "Global Quote": {
                "06. volume": "1000",
                "05. price": "150.0",
                "10. change percent": "5.0",
            }
        }

        prep_response = MagicMock()
        prep_response.status_code = 200
        prep_response.json.return_value = [
            {"companyName": "Apple Inc.", "mktCap": "2000000"}
        ]

        mock_get.side_effect = [alpha_response, prep_response]

        stock_data = self.stock_api_client.get_data()

        expected_stock_data = {
            "AAPL": {
                "volume": "1000",
                "price": "150.0",
                "change_percent": "5.0",
                "market_cap": "2000000",
                "name": "Apple Inc.",
            }
        }

        self.assertEqual(stock_data, expected_stock_data)

    @patch("core.stock_api_client.requests.get")
    def test_get_alpha_data_invalid_data(
        self,
        mock_get,
    ):
        alpha_response = MagicMock()
        alpha_response.status_code = 200
        alpha_response.json.return_value = {
            "Quote": {
                "06. volume": "1000",
                "05. price": "150.0",
                "10. change percent": "5.0",
            }
        }

        prep_response = MagicMock()
        prep_response.status_code = 200
        prep_response.json.return_value = [
            {"companyName": "Apple Inc.", "mktCap": "2000000"}
        ]

        mock_get.side_effect = [alpha_response, prep_response]

        with patch.object(self.logger, "error"):
            with self.assertRaises(KeyError):
                self.stock_api_client.get_data()

    @patch("core.stock_api_client.requests.get")
    def test_get_prep_data_invalid_data(self, mock_get):
        alpha_response = MagicMock()
        alpha_response.status_code = 200
        alpha_response.json.return_value = {
            "Global Quote": {
                "06. volume": "1000",
                "05. price": "150.0",
                "10. change percent": "5.0",
            }
        }

        prep_response = MagicMock()
        prep_response.status_code = 200
        prep_response.json.return_value = [{"company": "Name"}]

        mock_get.side_effect = [alpha_response, prep_response]

        with patch.object(self.logger, "error"):
            with self.assertRaises(KeyError):
                self.stock_api_client.get_data()

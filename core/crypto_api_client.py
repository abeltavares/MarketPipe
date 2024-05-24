import requests
import logging
from dotenv import load_dotenv
import os
from core.base_api import BaseApiClient
from pysertive import invariant
from utils import read_json, validate_symbols


COIN_BASE_URL = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?"


load_dotenv()


@invariant(validate_symbols, exception_type=ValueError, message="No Assets Provided")
class CryptoApiClient(BaseApiClient):
    """
    A client for retrieving cryptocurrency data from the CoinMarketCap API.

    This class inherits from the BaseApiClient abstract base class and implements the get_data method.

    Attributes:
        logger (logging.Logger): The logger object for logging messages.

    Methods:
        __init__(self, COIN_API_KEY: str, logger: logging.Logger): Initializes a new instance of the CryptoApiClient class.
    """

    def __init__(self, logger: logging.Logger):
        """
        Initializes a new instance of the CryptoApiClient class.

        Args:
            logger (logging.Logger): The logger object for logging messages.
        """
        super().__init__(logger=logger)
        self.symbols = read_json("mdp_config.json")["assets"]["cryptos"]["symbols"]

    def get_data(self) -> dict[str, dict[str, any]]:
        """
        Retrieves market data for the given list of symbols from CoinMarketCap API.

        Returns:
            Dict[str, Dict[str, str]]: A dictionary containing the retrieved data for each symbol.
        """
        parameters = {
            "start": "1",
            "limit": "100",
            "convert": "USD",
            "sort": "percent_change_24h",
        }
        print(os.getenv("COIN_API_KEY"))
        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": os.getenv("COIN_API_KEY"),
        }

        crypto_data = {}

        for symbol in self.symbols:
            try:
                # parameters["symbol"] = symbol

                response = requests.get(
                    COIN_BASE_URL, headers=headers, params=parameters
                )
                response.raise_for_status()

                data = response.json()
                symbol_data = data.get("data", [])[0]

                symbol_info = {
                    "name": symbol_data.get("name", ""),
                    "volume": symbol_data["quote"]["USD"].get("volume_24h", ""),
                    "price": symbol_data["quote"]["USD"].get("price", ""),
                    "change_percent": symbol_data["quote"]["USD"].get(
                        "percent_change_24h", ""
                    ),
                    "market_cap": symbol_data["quote"]["USD"].get("market_cap", ""),
                }

                crypto_data[symbol] = symbol_info

                self.logger.info(f"Successfully retrieved data for symbol {symbol}.")
            except requests.exceptions.RequestException as req_error:
                self.logger.error(f"Error during API request for {symbol}: {req_error}")
                raise
            except (IndexError, KeyError) as data_error:
                self.logger.error(f"Error processing data for {symbol}: {data_error}")
                raise

        return crypto_data


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    client = CryptoApiClient(logger)
    data = client.get_data()
    print(data)

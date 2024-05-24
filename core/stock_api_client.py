import os
import requests
import logging
from dotenv import load_dotenv
from core.base_api import BaseApiClient
from pysertive import invariant
from utils import read_json, validate_symbols

ALPHA_BASE_URL = "https://www.alphavantage.co/query?"
PREP_BASE_URL = "https://financialmodelingprep.com/api/v3/"

load_dotenv()


@invariant(validate_symbols, exception_type=ValueError, message="No Assets Provided")
class StockApiClient(BaseApiClient):
    """
    A client for retrieving stock data from multiple APIs.

    Attributes:
        logger (logging.Logger): The logger object for logging messages.

    Methods:
        get_data(symbols: List[str]) -> Dict[str, List[Dict[str, any]]]: Retrieves market data for the given list of symbols.
    """

    def __init__(self, logger: logging.Logger):
        """
        Initializes a new instance of the StockApiClient class.

        Args:
            logger (logging.Logger, optional): The logger object for logging messages. Defaults to None.
        """
        super().__init__(logger=logger)
        self.symbols = read_json("mdp_config.json")["assets"]["stocks"]["symbols"]
        print(self.symbols)

    def get_data(self) -> dict[str, dict[str, any]]:
        """
        Retrieves market data for the given list of symbols from Alpha Vantage and Financial Modeling Prep APIs.

        Returns:
            Dict[str, List[Dict]]: A dictionary containing the retrieved data for each symbol.
        """
        quote_endpoint = "GLOBAL_QUOTE"
        overview_endpoint = "profile"

        stock_data = {}

        for symbol in self.symbols:
            try:
                alpha_url = f"{ALPHA_BASE_URL}function={quote_endpoint}&symbol={symbol}&apikey={os.getenv('ALPHA_API_KEY')}"
                alpha_response = requests.get(alpha_url)
                alpha_response.raise_for_status()
                quote_data = alpha_response.json()

                if not quote_data["Global Quote"]:
                    self.logger.error(
                        f"No alpha data was retrieved for symbol {symbol}"
                    )
                    raise KeyError(f"No alpha data was retrieved for symbol {symbol}")

                volume = quote_data["Global Quote"]["06. volume"]
                price = quote_data["Global Quote"]["05. price"]
                change_percent = quote_data["Global Quote"]["10. change percent"]

                overview_url = f"{PREP_BASE_URL}{overview_endpoint}/{symbol}?apikey={os.getenv('PREP_API_KEY')}"
                prep_response = requests.get(overview_url)
                prep_response.raise_for_status()
                overview_data = prep_response.json()

                if (
                    not overview_data[0]["companyName"]
                    or not overview_data[0]["mktCap"]
                ):
                    self.logger.error(f"No prep data was retrieved for symbol {symbol}")
                    raise KeyError(f"No prep data was retrieved for symbol {symbol}")

                name = overview_data[0]["companyName"]
                market_cap = overview_data[0]["mktCap"]

                stock_data[symbol] = {
                    "volume": volume,
                    "price": price,
                    "change_percent": change_percent.rstrip("%"),
                    "market_cap": market_cap,
                    "name": name,
                }
                self.logger.info("Successfully retrieved stock data.")
            except requests.exceptions.RequestException as req_error:
                self.logger.error(f"Error during API request for {symbol}: {req_error}")
            except (ValueError, TypeError) as error:
                self.logger.error(
                    f"An error occurred while retrieving data for {symbol}: {error}"
                )

        return stock_data

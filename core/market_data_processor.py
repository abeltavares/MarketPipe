import psycopg2
from typing import Dict
import requests
import psycopg2
import logging
from typing import Dict, List
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
)

logger = logging.getLogger(__name__)


class BaseApiClient(ABC):

    # Define constant for the top gainers, losers, and actives
    TOP_PERFORMANCE_LIMIT = 5

    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    @abstractmethod
    def get_data(self) -> Dict[str, List[str]]:
        """
        Abstract method to get data. Child classes must implement this method.
        """
        pass


class StockApiClient(BaseApiClient):
    """
    A client for retrieving stock data from multiple APIs.

    Attributes:
        ALPHA_BASE_URL (str): The base URL for the Alpha Vantage API.
        PREP_BASE_URL (str): The base URL for the Financial Modeling Prep API.
        ALPHA_API_KEY (str): The API key for the Alpha Vantage API.
        PREP_API_KEY (str): The API key for the Financial Modeling Prep API.
        logger (logging.Logger): The logger object for logging messages.

    Methods:
        get_stocks(): Retrieves the symbols of the top 5 stocks for gainers, losers, and actives.
        get_data(symbols: Dict[str, List[str]]) -> Dict[str, List[Dict]]: Retrieves the volume, price, change percent, market cap, and name for the given symbols from Alpha Vantage's API.
    """

    ALPHA_BASE_URL = "https://www.alphavantage.co/query?"
    PREP_BASE_URL = "https://financialmodelingprep.com/api/v3/"

    def __init__(self, ALPHA_API_KEY: str, PREP_API_KEY: str, logger: logging.Logger):
        """
        Initializes a new instance of the StockApiClient class.

        Args:
            ALPHA_API_KEY (str): The API key for the Alpha Vantage API.
            PREP_API_KEY (str): The API key for the Financial Modeling Prep API.
            logger (logging.Logger, optional): The logger object for logging messages. Defaults to None.
        """
        super().__init__(logger=logger)
        self.ALPHA_API_KEY = ALPHA_API_KEY
        self.PREP_API_KEY = PREP_API_KEY

    def get_stocks(self) -> Dict[str, List[str]]:
        """
        Get the symbols of the top 5 stocks for gainers, losers, and actives.

        Returns:
            Dict[str, List[str]]: A dictionary with lists of symbols for gainers, losers, and actives.

        Raises:
            Exception: If any of the requests fails or if no data was retrieved.
        """
        # Define the URLs for the requested market performances
        urls = {
            "gainers": f"{self.PREP_BASE_URL}stock_market/gainers?apikey={self.PREP_API_KEY}",
            "losers": f"{self.PREP_BASE_URL}stock_market/losers?apikey={self.PREP_API_KEY}",
            "actives": f"{self.PREP_BASE_URL}stock_market/actives?apikey={self.PREP_API_KEY}",
        }

        # Initialize the dictionary to store the stocks
        stocks = {"gainers": [], "losers": [], "actives": []}

        # Send a GET request to each URL
        for performance, url in urls.items():
            try:
                response = requests.get(url, timeout=5)

                # Check if the request was successful
                response.raise_for_status()

                # Retrieve the data from the API response
                data = response.json()

                # Check if the data is empty
                if not data:
                    self.logger.error(f"No data was retrieved for '{performance}'")
                    raise ValueError(f"No data was retrieved for '{performance}'")

                # Get symbol of top stocks in the specified market performance
                stock_symbols = [
                    item["symbol"] for item in data[: self.TOP_PERFORMANCE_LIMIT]
                ]

                # Store the stocks in the dictionary
                stocks[performance] = stock_symbols
                self.logger.info(f"Successfully retrieved stocks for '{performance}'.")
            except requests.exceptions.RequestException as req_error:
                self.logger.error(
                    f"Error during API request for '{performance}': {req_error}"
                )
                raise
            except (ValueError, IndexError, KeyError, TypeError) as data_error:
                self.logger.error(
                    f"Error processing data for '{performance}': {data_error}"
                )
                raise

        return stocks

    def get_data(self, symbols: Dict[str, List[str]]) -> Dict[str, List[Dict]]:
        """
        Retrieves the volume, price, change percent, market cap, and name for the given symbols from Alpha Vantage's API.

        Args:
            symbols (Dict[str, List[str]]): A dictionary of symbols for the stocks to retrieve data for, with the symbol type (gainers, losers, actives) as the key and a list of symbols as the value.

        Returns:
            Dict[str, List[Dict]]: A dictionary of dictionaries for each symbol type (gainers, losers, actives) with the symbol as the key and a dictionary of volume, price, change percent, market cap, and name as the value.
        """
        quote_endpoint = "GLOBAL_QUOTE"
        overview_endpoint = "profile"

        stock_data = {}

        for symbol_type, symbol_list in symbols.items():
            stock_data[symbol_type] = []
            for symbol in symbol_list:
                try:
                    # Build the URL to request data for the given symbol from the global quote endpoint
                    alpha_url = f"{self.ALPHA_BASE_URL}function={quote_endpoint}&symbol={symbol}&apikey={self.ALPHA_API_KEY}"
                    # Request data from the API and convert the response to a dictionary
                    alpha_response = requests.get(alpha_url)
                    alpha_response.raise_for_status()  # Raise an error for unsuccessful responses
                    quote_data = alpha_response.json()

                    if not quote_data["Global Quote"]:
                        self.logger.error(
                            f"No alpha data was retrieved for symbol {symbol}"
                        )
                        raise KeyError(
                            f"No alpha data was retrieved for symbol {symbol}"
                        )

                    # Extract the volume, price, and change percent data from the response
                    volume = quote_data["Global Quote"]["06. volume"]
                    price = quote_data["Global Quote"]["05. price"]
                    change_percent = quote_data["Global Quote"]["10. change percent"]

                    # Build the URL to request data for the given symbol from the profile endpoint
                    overview_url = f"{self.PREP_BASE_URL}{overview_endpoint}/{symbol}?apikey={self.PREP_API_KEY}"
                    # Request data from the API and convert the response to a dictionary
                    prep_response = requests.get(overview_url)
                    prep_response.raise_for_status()  # Raise an error for unsuccessful responses
                    overview_data = prep_response.json()

                    if (
                        not overview_data[0]["companyName"]
                        or not overview_data[0]["mktCap"]
                    ):
                        self.logger.error(
                            f"No prep data was retrieved for symbol {symbol}"
                        )
                        raise KeyError(
                            f"No prep data was retrieved for symbol {symbol}"
                        )

                    # Extract the name and market cap data from the response
                    name = overview_data[0]["companyName"]
                    market_cap = overview_data[0]["mktCap"]

                    # Append the data to the stock_data list
                    stock_data[symbol_type].append(
                        {
                            "symbol": symbol,
                            "volume": volume,
                            "price": price,
                            "change_percent": change_percent.rstrip("%"),
                            "market_cap": market_cap,
                            "name": name,
                        }
                    )
                    self.logger.info("Successfully retrieved stock data.")
                except requests.exceptions.RequestException as req_error:
                    self.logger.error(
                        f"Error during API request for {symbol}: {req_error}"
                    )
                except (ValueError, TypeError) as error:
                    self.logger.error(
                        f"An error occurred while retrieving data for {symbol}: {error}"
                    )

        return stock_data


class CryptoApiClient(BaseApiClient):
    def __init__(self, COIN_API_KEY: str, logger: logging.Logger = None):
        super().__init__(logger=logger)
        self.COIN_API_KEY = COIN_API_KEY

    def get_data(self) -> Dict[str, List[Dict]]:
        """
        Gets the top gainers, losers, and active cryptocurrencies on CoinMarketCap.

        Returns:
            dict: A dictionary containing the top gainers, losers, and most active cryptocurrencies.
        """
        # Define the API endpoint
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

        # Set the parameters for the API request
        parameters = {
            "start": "1",
            "limit": "100",
            "convert": "USD",
            "sort": "percent_change_24h",
        }

        # Add the API key to the request headers
        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": self.COIN_API_KEY,
        }

        try:
            # Send the API request
            response = requests.get(url, headers=headers, params=parameters)

            # Check if the API request was successful
            response.raise_for_status()

            # Parse the response JSON data
            data = response.json()

            # Extract the top gainers, top losers, and top active cryptos
            top_gainers = data.get("data", [])[: self.TOP_PERFORMANCE_LIMIT]
            top_losers = data.get("data", [])[-self.TOP_PERFORMANCE_LIMIT :]
            top_active = sorted(
                data.get("data", []),
                key=lambda x: x["quote"]["USD"]["volume_24h"],
                reverse=True,
            )[: self.TOP_PERFORMANCE_LIMIT]

            # Create the dictionaries for gainers, losers, and active cryptos
            gainer_list = []
            loser_list = []
            active_list = []

            for gainer in top_gainers:
                try:
                    gainer_dict = {
                        "symbol": gainer.get("symbol", ""),
                        "name": gainer.get("name", ""),
                        "volume": gainer["quote"]["USD"].get("volume_24h", ""),
                        "price": gainer["quote"]["USD"].get("price", ""),
                        "change_percent": gainer["quote"]["USD"].get(
                            "percent_change_24h", ""
                        ),
                        "market_cap": gainer["quote"]["USD"].get("market_cap", ""),
                    }
                except KeyError as e:
                    self.logger.error(
                        f"KeyError while processing gainer data: {e}, Data: {gainer}"
                    )
                gainer_list.append(gainer_dict)

            for loser in top_losers:
                try:
                    loser_dict = {
                        "symbol": loser.get("symbol", ""),
                        "name": loser.get("name", ""),
                        "volume": loser["quote"]["USD"].get("volume_24h", ""),
                        "price": loser["quote"]["USD"].get("price", ""),
                        "change_percent": loser["quote"]["USD"].get(
                            "percent_change_24h", ""
                        ),
                        "market_cap": loser["quote"]["USD"].get("market_cap", ""),
                    }
                except KeyError as e:
                    self.logger.error(
                        f"KeyError while processing loser data: {e}, Data: {loser}"
                    )
                loser_list.append(loser_dict)

            for active in top_active:
                try:
                    active_dict = {
                        "symbol": active.get("symbol", ""),
                        "name": active.get("name", ""),
                        "volume": active["quote"]["USD"].get("volume_24h", ""),
                        "price": active["quote"]["USD"].get("price", ""),
                        "change_percent": active["quote"]["USD"].get(
                            "percent_change_24h", ""
                        ),
                        "market_cap": active["quote"]["USD"].get("market_cap", ""),
                    }
                except KeyError as e:
                    self.logger.error(
                        f"KeyError while processing active data: {e}, Data: {active} "
                    )
                active_list.append(active_dict)

            self.logger.info("Successfully retrieved crypto data.")
            return {
                "gainers": gainer_list,
                "losers": loser_list,
                "actives": active_list,
            }

        except requests.exceptions.RequestException as req_error:
            self.logger.error(
                f"Error during API request for cryptocurrencies: {req_error}"
            )
            return None
        except ValueError as data_error:
            self.logger.error(
                f"Error processing data for cryptocurrencies: {data_error}"
            )
            return None


class Storage:
    """
    A class that handles storing data in a database.

    Attributes:
        host (str): The host address of the database.
        port (int): The port number of the database.
        database (str): The name of the database.
        user (str): The username for accessing the database.
        password (str): The password for accessing the database.
        logger (logging.Logger): The logger object for logging messages.
        conn: The database connection object.
        cur: The database cursor object.
    """

    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
        logger: logging.Logger = logger,
    ):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.logger = logger
        self.conn = None
        self.cur = None

    def _connect(self):
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
            )
            self.cur = self.conn.cursor()
        except psycopg2.Error as e:
            self.logger.error(f"Error connecting to the database: {e}")
            raise

    def _close(self):
        try:
            if self.cur:
                self.cur.close()
            if self.conn:
                self.conn.close()
        except psycopg2.Error as e:
            self.logger.error(f"Error closing the database connection: {e}")

    def store_data(self, data: Dict[str, List[Dict[str, any]]], data_type: str) -> None:
        try:
            # Check if data_type is a string
            if not isinstance(data_type, str):
                self.logger.error("data_type must be a string")
                raise TypeError("data_type must be a string")

            self.logger.info(f"Storing {data_type} data in the database.")

            self._connect()
            schema_name = f"{data_type}_data"
            with self.conn, self.cur:
                for key, asset_list in data.items():
                    table = f"{schema_name}.{key}"
                    for asset_data in asset_list:
                        symbol = asset_data["symbol"]
                        name = asset_data["name"]
                        volume = asset_data["volume"]
                        price = asset_data["price"]
                        market_cap = asset_data["market_cap"]
                        change_percent = asset_data["change_percent"]

                        if not all([symbol, name]):
                            self.logger.error(
                                f"One or more required fields are missing from the {data_type} data for symbol: {symbol}, name: {name}"
                            )
                            raise ValueError(
                                f"One or more required fields are missing from the {data_type} data"
                            )

                        self.cur.execute(
                            f"INSERT INTO {table} (symbol, name, market_cap, volume, price, change_percent) VALUES (%s, %s, %s, %s, %s, %s)",
                            (symbol, name, market_cap, volume, price, change_percent),
                        )
                    self.conn.commit()
                    # Log a message for successful data storage
                    self.logger.info(
                        f"Successfully stored {len(asset_list)} entries in the {table} table."
                    )
        except psycopg2.Error as error:
            self.logger.error(
                f"An error occurred while storing the {data_type} data in the database: {error}"
            )
            if self.conn:
                self.conn.rollback()
        finally:
            self._close()


class MarketDataEngine:
    """
    Class representing a market data engine.

    Attributes:
        api_client (BaseApiClient): The API client used to fetch market data.
        db_connector (Storage): The database connector used to store market data.
        logger (logging.Logger): The logger used for logging.

    Methods:
        process_stock_data: Fetches stock data from the API client and stores it in the database.
        process_crypto_data: Fetches crypto data from the API client and stores it in the database.
    """

    def __init__(
        self,
        api_client: BaseApiClient,
        db_connector: "Storage",
        logger: logging.Logger = logger,
    ):
        self.api_client = api_client
        self.db_connector = db_connector
        self.logger = logger

    def process_stock_data(self):
        """
        Fetches stock data from the API client and stores it in the database.
        If the stock data retrieval fails, a warning message is logged.
        """
        try:
            stocks = self.api_client.get_stocks()
            stock_data = self.api_client.get_data(stocks)
            if stock_data is not None:
                self.db_connector.store_data(stock_data, "stock")
            else:
                self.logger.warning(
                    "Stock data retrieval failed. No data stored in the database."
                )
        except Exception as e:
            self.logger.error(f"Error processing stock data: {e}")

    def process_crypto_data(self):
        """
        Fetches crypto data from the API client and stores it in the database.
        If the crypto data retrieval fails, a warning message is logged.
        """
        try:
            crypto_data = self.api_client.get_data()
            if crypto_data is not None:
                self.db_connector.store_data(crypto_data, "crypto")
            else:
                self.logger.warning(
                    "Crypto data retrieval failed. No data stored in the database."
                )
        except Exception as e:
            self.logger.error(f"Error processing crypto data: {e}")

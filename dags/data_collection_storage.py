"""
A Python script with functions for retrieving stock and crypto performance data from Alpha Vantage, Financial Modeling Prep and CoinMarketCap APIs and storing the data in a PostgreSQL database.
"""

# Import necessary modules
import requests
import datetime
import time
import os
import psycopg2


# Define the base URL and API key for Alpha Advantage API
ALPHA_BASE_URL = "https://www.alphavantage.co/query?"
ALPHA_API_KEY = "S1HB81M1BIAB0ML2"  #replace with your API key

# Define the base URL and API key for Financial Modeling Prep API
PREP_BASE_URL = "https://financialmodelingprep.com/api/v3/"
PREP_API_KEY = "601e5192acccbaeee4ed7e15f16c1200"  #replace with your API key

# Define the API key for CoinMarketCap API
COIN_API_KEY = '08012b12-c8f6-482f-821d-0fa6dbce76e3'

# These variables are used to make API requests to Alpha Advantage, Financial Modeling Prep and CoinMarketCap 
# The base URL and API key are used to build the complete URL to make the request


def get_stocks() -> dict:
    """
    Get the symbols of the top 5 stocks for gainers, losers, and actives.
    :return: a dictionary with lists of symbols for gainers, losers, and actives
    :raise: Exception if any of the requests fails or if no data was retrieved
    """
    # Define the URLs for the requested market performances
    urls = {
        'gainers': f"{PREP_BASE_URL}stock_market/gainers?apikey={PREP_API_KEY}",
        'losers': f"{PREP_BASE_URL}stock_market/losers?apikey={PREP_API_KEY}",
        'actives': f"{PREP_BASE_URL}stock_market/actives?apikey={PREP_API_KEY}"
    }

    # Initialize the dictionary to store the stocks
    stocks = {'gainers': [], 'losers': [], 'actives': []}

    # Send a GET request to each URL
    for performance, url in urls.items():
        response = requests.get(url, timeout=5)

        # Check if the request was successful
        if response.status_code != 200:
            raise Exception(f"Failed to retrieve data from the API for '{performance}': {response.text}")

        # Retrieve the data from the API response
        data = response.json()

        # Check if the data is empty
        if not data:
            raise Exception(f"No data was retrieved for '{performance}'")

        # Get symbol of top 5 stocks in the specified market performance
        stock_symbols = [item['symbol'] for item in data[:5]]

        # Store the stocks in the dictionary
        stocks[performance] = stock_symbols

    return stocks


def get_stock_data(symbols: dict) -> dict:
    """
    Retrieves the volume, price, change percent, market cap, and name for the given symbols from Alpha Vantage's API.
    :param symbols: A dictionary of symbols for the stocks to retrieve data for, with the symbol type (gainers, losers, actives) as the key and a list of symbols as the value
    :return: A dictionary of dictionaries for each symbol type (gainers, losers, actives) with the symbol as the key and a dictionary of volume, price, change percent, market cap, and name as the value
    """
    quote_endpoint = "GLOBAL_QUOTE"
    overview_endpoint = "profile"
    stock_data = {}
    for symbol_type, symbol_list in symbols.items():
        stock_data[symbol_type] = []
        for symbol in symbol_list:
            try:
                # Build the URL to request data for the given symbol from the global quote endpoint 
                alpha_url = f"{ALPHA_BASE_URL}function={quote_endpoint}&symbol={symbol}&apikey={ALPHA_API_KEY}"
                # Request data from the API and convert the response to a dictionary
                alpha_response = requests.get(alpha_url)
                quote_data = alpha_response.json()

                # Validate the data returned from the API
                if "Error Message" in quote_data:
                    raise ValueError(f"Error retrieving data for symbol {symbol}: {quote_data['Error Message']}")

                # Extract the volume, price, and change percent data from the response
                volume = quote_data["Global Quote"]["06. volume"]
                price = quote_data["Global Quote"]["05. price"]
                change_percent = quote_data["Global Quote"]["10. change percent"]

                # Build the URL to request data for the given symbol from the profile endpoint
                overview_url = f"{PREP_BASE_URL}{overview_endpoint}/{symbol}?apikey={PREP_API_KEY}"
                # Request data from the API and convert the response to a dictionary
                prep_response = requests.get(overview_url)
                overview_data = prep_response.json()

                # Validate the data returned from the API
                if "Error Message" in overview_data:
                    raise ValueError(f"Error retrieving data for symbol {symbol}: {quote_data['Error Message']}")

                # Extract the name and market cap data from the response
                name = overview_data[0]['companyName']
                market_cap = overview_data[0]['mktCap']

                # Append the data to the stock_data list
                stock_data[symbol_type].append({
                    "symbol": symbol,
                    "volume": volume,
                    "price": price,
                    "change_percent": change_percent.rstrip('%'),
                    "market_cap": market_cap,
                    "name": name
                })
            except (ValueError, KeyError) as error:
                print(f"An error occurred while retrieving data for symbol {symbol}: {error}")
        # Pause until the next full minute
        time.sleep(55)
    return stock_data


def store_stock_data(data: dict):
    """
    Store the stock market data in a PostgreSQL database
    :param data: A dictionary with keys 'gainers', 'losers', and 'actives', each with a list of stock data
    """

    # Set the schema name to use for storing the stock data
    schema_name = "stock_data"

    # Get the database configuration from environment variables
    host = os.environ.get("POSTGRES_HOST")
    port = os.environ.get("POSTGRES_PORT")
    database = os.environ.get("POSTGRES_DB")
    user = os.environ.get("POSTGRES_USER")
    password = os.environ.get("POSTGRES_PASSWORD")

    # Connect to the database
    conn = None
    cur = None
    try:
        # Connect to the database using the configuration from environment variables
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )

        # Create a cursor to execute SQL queries
        cur = conn.cursor()
        
        # Loop through the stock data for each key in the dictionary
        for key, stock_list in data.items():
            # Create a table name based on the key name
            table = f"{schema_name}.{key}"
            # Loop through the stock data
            for stock_data in stock_list:
                # Extract the relevant information
                symbol = stock_data["symbol"]
                name = stock_data["name"]
                volume = stock_data["volume"]
                price = stock_data["price"]
                market_cap = stock_data["market_cap"]
                change_percent = stock_data["change_percent"]

                # Validate the data
                if not all([symbol, name]):
                    raise ValueError("One or more required fields are missing from the stock data")

                # Insert the data into the table
                cur.execute(f"INSERT INTO {table} (symbol, name, market_cap, volume, price, change_percent) VALUES (%s, %s, %s, %s, %s, %s)",
                            (symbol, name, market_cap, volume, price, change_percent))

            # Commit the changes to the database
            conn.commit()
    except (psycopg2.Error, ValueError, TypeError) as error:
        print(f"An error occurred while storing the data in the database: {error}")
        # Rollback the changes if there was an error
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def get_crypto_data() -> dict:
    """
    Gets the top gainers, losers, and active cryptocurrencies on CoinMarketCap.

    Returns:
        dict: A dictionary containing the top gainers, losers, and most active cryptocurrencies.
    """
    # Define the API endpoint
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

    # Set the parameters for the API request
    parameters = {
        'start': '1',
        'limit': '100',
        'convert': 'USD',
        'sort': 'percent_change_24h'
    }

    # Add the API key to the request headers
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': COIN_API_KEY
    }

    try:
        # Send the API request
        response = requests.get(url, headers=headers, params=parameters)

        # Check if the API request was successful
        if response.status_code == 200:
            # Parse the response JSON data
            data = response.json()

            # Extract the top gainers, top losers, and top active cryptos
            top_gainers = data['data'][:5]
            top_losers = data['data'][-5:]
            top_active = sorted(data['data'], key=lambda x: x['quote']['USD']['volume_24h'], reverse=True)[:5]

            # Create the dictionaries for gainers, losers, and active cryptos
            gainer_list = []
            loser_list = []
            active_list = []

            for gainer in top_gainers:
                gainer_dict = {
                    'symbol': gainer['symbol'],
                    'name': gainer['name'],
                    'volume': gainer['quote']['USD']['volume_24h'],
                    'price': gainer['quote']['USD']['price'],
                    'change_percent': gainer['quote']['USD']['percent_change_24h'],
                    'market_cap': gainer['quote']['USD']['market_cap']
                }
                gainer_list.append(gainer_dict)

            for loser in top_losers:
                loser_dict = {
                    'symbol': loser['symbol'],
                    'name': loser['name'],
                    'volume': loser['quote']['USD']['volume_24h'],
                    'price': loser['quote']['USD']['price'],
                    'change_percent': loser['quote']['USD']['percent_change_24h'],
                    'market_cap': loser['quote']['USD']['market_cap']
                }
                loser_list.append(loser_dict)

            for active in top_active:
                active_dict = {
                    'symbol': active['symbol'],
                    'name': active['name'],
                    'volume': active['quote']['USD']['volume_24h'],
                    'price': active['quote']['USD']['price'],
                    'change_percent': active['quote']['USD']['percent_change_24h'],
                    'market_cap': active['quote']['USD']['market_cap']
                }
                active_list.append(active_dict)

            return {'gainers': gainer_list, 'losers': loser_list, 'actives': active_list}
        else:
            print(f"Error: Request failed with status code {response.status_code}.")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


def store_crypto_data(data: dict):
    """
    Store the crypto market data in a PostgreSQL database
    :param data: A dictionary with keys 'gainers', 'losers', and 'actives', each with a list of crypto data
    """

    # Set the schema name to use for storing the crypto data
    schema_name = "crypto_data"

    # Get the database configuration from environment variables
    host = os.environ.get("POSTGRES_HOST")
    port = os.environ.get("POSTGRES_PORT")
    database = os.environ.get("POSTGRES_DB")
    user = os.environ.get("POSTGRES_USER")
    password = os.environ.get("POSTGRES_PASSWORD")

    # Connect to the database
    conn = None
    cur = None
    try:
        # Connect to the database using the configuration from environment variables
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )

        # Create a cursor to execute SQL queries
        cur = conn.cursor()

        # Loop through the crypto data for each key in the dictionary
        for key, crypto_list in data.items():
            # Create a table name based on the key name
            table = f"{schema_name}.{key}"
            # Loop through the crypto data
            for crypto_data in crypto_list:
                # Extract the relevant information
                symbol = crypto_data["symbol"]
                name = crypto_data["name"]
                volume = crypto_data["volume"]
                price = crypto_data["price"]
                market_cap = crypto_data["market_cap"]
                change_percent = crypto_data["change_percent"]
                print(change_percent)

                # Validate the data
                if not all([symbol, name]):
                    raise ValueError("One or more required fields are missing from the crypto data")

                # Insert the data into the table
                cur.execute(f"INSERT INTO {table} (symbol, name, market_cap, volume, price, change_percent) VALUES (%s, %s, %s, %s, %s, %s)",
                            (symbol, name, market_cap, volume, price, change_percent))

            # Commit the changes to the database
            conn.commit()
    except (psycopg2.Error, ValueError, TypeError) as error:
        print(f"An error occurred while storing the data in the database: {error}")
        # Rollback the changes if there was an error
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
 
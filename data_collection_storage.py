"""
A Python script that retrieves stock market data from Alpha Vantage and Financial Modeling Prep APIs and stores the data in a PostgreSQL database.

The script contains three main functions:
- `get_stocks`: retrieves the symbols of the top 5 stocks of a specified market performance (gainers, losers, or actives)
- `get_stock_data`: retrieves the volume, price, change percent, and name of the specified stock symbols
- `store_stock_data_in_database`: stores the stock market data in a PostgreSQL database
"""
import requests
import psycopg2
import json

# Define the base URL and API key for Alpha Advantage API
ALPHA_BASE_URL = "https://www.alphavantage.co/query?"
ALPHA_API_KEY = "S1HB81M1BIAB0ML2"

# Define the base URL and API key for Financial Modeling Prep API

PREP_BASE_URL = "https://financialmodelingprep.com/api/v3/"
PREP_API_KEY = "e18f8efccbac4ac741c48162fec73d2e"

# These variables are used to make API requests to both Alpha Advantage and Financial Modeling Prep
# The base URL and API key are used to build the complete URL to make the request

def get_stocks(market_performance: str) -> list:
    """
    Get the symbols of the top 5 stocks of the specified market performance.

    :param market_performance: string indicating the type of market data to retrieve (Gainers, losers, or actives)
    :return: a list of symbols of the top 5 stocks in the specified market performance
    :raise: Exception if the request fails or if no data was retrieved
    """
    # Define the URL for the requested market performance
    url = f"{PREP_BASE_URL}stock_market/{market_performance}?apikey={PREP_API_KEY}"

    # Send a GET request to the API
    response = requests.get(url, timeout=5)

    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve data from the API: {response.text}")

    # Retrieve the data from the API response
    data = response.json()

    # Check if the data is empty
    if not data:
        raise Exception(f"No data was retrieved for market performance '{market_performance}'")

    # Get symbol of top 5 stocks in the specified market performance
    stock_symbols = [item['symbol'] for item in data[:5]]

    return stock_symbols

def get_stock_data(symbols: list) -> dict:
    """
    This function retrieves the volume, price, change percent, and name for the given symbols from Alpha Vantage's API.

    :param symbols: A list of symbols for the stocks to retrieve data for
    :return: A dictionary with the symbol as the key and a dictionary of volume, price, change percent, and name as the value
    """
    alpha_endpoint = "GLOBAL_QUOTE"
    prep_endpoint = "profile"
    stock_data = {}
    for symbol in symbols:
        try:
            # Build the URL to request data for the given symbol from the global quote endpoint 
            alpha_url = f"{ALPHA_BASE_URL}function={alpha_endpoint}&symbol={symbol}&apikey={ALPHA_API_KEY}"
            # Request data from the API and convert the response to a dictionary
            alpha_response = requests.get(alpha_url)
            alpha_data = alpha_response.json()

            # Validate the data returned from the API
            if "Error Message" in alpha_data:
                raise ValueError(f"Error retrieving data for symbol {symbol}: {alpha_data['Error Message']}")

            # Extract the volume, price, and change percent data from the response
            volume = alpha_data["Global Quote"]["06. volume"]
            price = alpha_data["Global Quote"]["05. price"]
            change_percent = alpha_data["Global Quote"]["10. change percent"]

            # Build the URL to request data for the given symbol from the profile endpoint
            prep_url = f"{PREP_BASE_URL}{prep_endpoint}/{symbol}?apikey={PREP_API_KEY}"
            # Request data from the API and convert the response to a dictionary
            prep_response = requests.get(prep_url)
            prep_data = prep_response.json()

            # Validate the data returned from the API
            if not prep_data:
                raise ValueError(f"Error retrieving name for symbol {symbol}")

            # Extract the name data from the response
            name = prep_data[0]['companyName']

            # Store the data in the stock_data dictionary
            stock_data[symbol] = {
                "volume": int(volume),
                "price": float(price),
                "change_percent": float(change_percent.rstrip('%')),
                "name": name,
            }
        except (ValueError, KeyError) as error:
            print(f"An error occurred while retrieving data for symbol {symbol}: {error}")

    return stock_data 

def store_stock_data_in_database(data: dict, config_file: str):
    """
    Store the stock market data in a PostgreSQL database
    :param data: A dictionary with the stock symbol as the key and the stock data as the value
    :param config_file: A JSON file containing the database configuration
    """
    # Load the database configuration
    with open(config_file, "r") as f:
        config = json.load(f)
    host = config.get("host")
    database = config.get("database")
    user = config.get("user")
    password = config.get("password")
    schema_name = config.get("schema_name")
    table_name = config.get("table_name")

    # Connect to the database
    conn = None
    cur = None
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=config["host"],
            database=config["database"],
            user=config["user"],
            password=config["password"]
        )
        cur = conn.cursor()
        # Loop through the stock data
        for symbol, stock_data in data.items():
            # Extract the relevant information
            name = stock_data.get("name")
            volume = stock_data.get("volume")
            price = stock_data.get("price")
            change_percent = stock_data.get("change_percent")

            # Validate the data
            if not all([symbol, name, volume, price, change_percent]):
                raise ValueError("One or more required fields are missing from the stock data")
            if not isinstance(volume, int):
                raise TypeError("Volume must be of type int")
            if not isinstance(price, float):
                raise TypeError("Price must be of type float")
            if not isinstance(change_percent, float):
                raise TypeError("Change percent must be of type float")

            # Insert the data into the table
            cur.execute(f"INSERT INTO {schema_name} . {table_name} (symbol, name, volume, price, change_percent) VALUES (%s, %s, %s, %s, %s)",
                       (symbol, name, volume, price, change_percent))

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
            

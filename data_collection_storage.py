"""This module contains functions for collecting and storing stock data."""
import datetime
import requests
import psycopg2


# Function for retrieving top gainers
def get_top_gainers():
    """Get the top gainers from the financialmodelingprep API"""
    url = "https://financialmodelingprep.com/api/v3/stock_market/gainers?apikey=e18f8efccbac4ac741c48162fec73d2e"
    response = requests.get(url, timeout=5)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve data from the API: {response.text}")
    data = response.json()
    return data

# Function for retrieving company name
def get_company_name(symbol):
    """Get the name from the company profile information"""
    url = f"https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey=e18f8efccbac4ac741c48162fec73d2e"
    response = requests.get(url, timeout=5)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve data for {symbol} from the API: {response.text}")
    company_data = response.json()[0]['companyName']
    # Return the company name
    return company_data

# List of the 5 top gainers
top_gainers_data = get_top_gainers()
top_five_stocks = []
for i in range(5):
    top_five_stocks.append(top_gainers_data[i]["symbol"])


# Function for retrieving top stock data
def get_stock_data(symbols):
    """Get the stock data for a list of symbols from the Alpha Vantage API"""
    stock_info = {}
    for symbol in symbols:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey=S1HB81M1BIAB0ML2'
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            raise Exception(f"Failed to retrieve data for {symbol} from the API: {response.text}")
        stock_info[symbol] = response.json()
    return stock_info

# Call the function to retrieve data for the 5 top gainers
stock_data = get_stock_data(top_five_stocks)

def store_data_in_postgresql(data):
    """Store the stock data in a PostgreSQL database"""
    # Connect to the database
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="dashdata",
            user="abel",
            password="password"
        )
        cur = conn.cursor()

        # Loop through the stock data
        for symbol, stock_info in data.items():
            # Get the company name for the symbol
            name = get_company_name(symbol)

            # Extract the relevant information
            date = datetime.datetime.strptime(stock_info["Meta Data"]["3. Last Refreshed"], \
                 '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            open_price = stock_info["Time Series (5min)"][date]["1. open"]
            high = stock_info["Time Series (5min)"][date]["2. high"]
            low = stock_info["Time Series (5min)"][date]["3. low"]
            close_price = stock_info["Time Series (5min)"][date]["4. close"]
            volume = stock_info["Time Series (5min)"][date]["5. volume"]
            # Insert the data into the table
            cur.execute("INSERT INTO dashboard.stock_data \
                (symbol, name, date, open, high, low, close, volume) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (symbol, name, date, open_price, high, low, close_price, volume))
        conn.commit()
    except psycopg2.Error as error:
        print(f"An error occurred while storing the data in the database: {error}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# Call the function to store the stock data
store_data_in_postgresql(stock_data)

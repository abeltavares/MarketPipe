-- Create the schema
CREATE SCHEMA IF NOT EXISTS market_data;


-- Create a table for stock data
CREATE TABLE IF NOT EXISTS market_data.stocks (
    id SERIAL PRIMARY KEY,
    date_collected DATE NOT NULL DEFAULT CURRENT_DATE,
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(50) NOT NULL,
    market_cap DECIMAL(20,2) NOT NULL,
    volume INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    change_percent DECIMAL(15,8) NOT NULL
);

-- Create a table for cryptocurrency data
CREATE TABLE IF NOT EXISTS market_data.cryptos (
    id SERIAL PRIMARY KEY,
    date_collected DATE NOT NULL DEFAULT CURRENT_DATE,
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(50) NOT NULL,
    market_cap DECIMAL(20,2) NOT NULL,
    volume INT NOT NULL,
    price DECIMAL(25,15) NOT NULL,
    change_percent DECIMAL(50,30) NOT NULL
);

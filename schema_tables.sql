-- Create a database
CREATE DATABASE stock_data_db;
\c stock_data_db

-- Create a schema for the project
CREATE SCHEMA stock_data;

-- Create a table to store the stock data
CREATE TABLE stock_data.stocks (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    name VARCHAR(50) NOT NULL,
    volume INT NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    change_percent NUMERIC(5,2) NOT NULL,
    date_collected TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

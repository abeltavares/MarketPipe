-- Create a schema for the project
CREATE SCHEMA dashboard;

-- Create a table to store the stock data
CREATE TABLE IF NOT EXISTS dashboard.stock_data (
  id serial PRIMARY KEY,
  symbol varchar(50) NOT NULL,
  date timestamp NOT NULL,
  open numeric(10, 2) NOT NULL,
  high numeric(10, 2) NOT NULL,
  low numeric(10, 2) NOT NULL,
  close numeric(10, 2) NOT NULL,
  volume numeric(10, 2) NOT NULL
);

-- Create a table to store the crypto data
CREATE TABLE IF NOT EXISTS dashboard.crypto_data (
  id serial PRIMARY KEY,
  symbol varchar(50) NOT NULL,
  date timestamp NOT NULL,
  open numeric(10, 2) NOT NULL,
  high numeric(10, 2) NOT NULL,
  low numeric(10, 2) NOT NULL,
  close numeric(10, 2) NOT NULL,
  volume numeric(10, 2) NOT NULL
);  

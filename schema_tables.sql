-- Create a schema for the project
CREATE SCHEMA dashboard_data;

-- Create a table to store the stock data
CREATE TABLE IF NOT EXISTS dashboard_data.stock_data (
  id serial PRIMARY KEY,
  stock varchar(50) NOT NULL,
  name varchar(255) NOT NULL,
  date timestamp NOT NULL,
  open numeric(10, 2) NOT NULL,
  high numeric(10, 2) NOT NULL,
  low numeric(10, 2) NOT NULL,
  close numeric(10, 2) NOT NULL,
  volume numeric(10, 2) NOT NULL
);

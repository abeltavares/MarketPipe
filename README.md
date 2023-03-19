![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=Docker&logoColor=white)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=for-the-badge&logo=Apache%20Airflow&logoColor=white)
![PgAdmin](https://img.shields.io/badge/PgAdmin-4B0082?style=for-the-badge&logo=pgAdmin&logoColor=white)


[![Powered by PostgreSQL](https://img.shields.io/badge/powered%20by-PostgreSQL-blue.svg)](https://www.postgresql.org/)
[![Python Version](https://img.shields.io/badge/python-3.x-brightgreen.svg)](https://www.python.org/downloads/)


# MarketTrackPipe

MarketTrackPipe is an automated Apache Airflow data pipeline for collecting, storing, and backing up stock and cryptocurrency market data. The pipeline retrieves daily data for the top 5 stocks and top 5 cryptocurrencies based on market performance from Alpha Vantage, Financial Modeling Prep, and CoinMarketCap APIs and stores it in a PostgreSQL database. Additionally, the pipeline includes a monthly backup function that stores the data from the database in an AWS S3 bucket. The pipeline is containerized using Docker and written in Python 3.

## Project Components

The pipeline consists of two Python scripts in `dags` folder:

- `data_collection_storage.py`: Contains functions for retrieving stock and crypto performance data from APIs and storing the data in a PostgreSQL database, as well as a function for backing up the data to Amazon S3.
- `market_data_dag.py`:  Sets up the DAGs for collecting and storing stock data from the financialmodelingprep and Alpha Advantage APIs, as well as cryptocurrency data from the CoinMarketCap API. Additionally, it sets up a DAG for backing up the data in the PostgreSQL database to Amazon S3 on the last day of every month.

The `data_collection_storage_stocks` DAG consists of the following tasks:

1. `get_stocks`: Retrieves the symbol of the top 5 stocks according to market performance.

2. `get_stock_data`: Retrieves detailed information of the stocks retrieved in task 1.

3. `store_stock_data`: Stores the stock data in a PostgreSQL database.

DAG runs every day at 11 PM from Monday to Friday.

The `data_collection_storage_crypto` DAG consists of the following tasks:

1. `get_crypto_data`: Retrieves data for the top 5 cryptocurrencies according to market performance.

2. `store_crypto_data`: Stores the cryptocurrency data in a PostgreSQL database.

DAG runs every day at 11 PM.

The `backup_data` DAG consists of the following task:

1. `backup_data`: Extracts data from the PostgreSQL database and stores it in an Amazon S3 bucket in parquet file format.

The `docker-compose.yml` file is used to define the services and configure the project's containers, setting up the environment (postgres, pgadmin, airflow).

The `init.sql` file is used to create and initialize the database schema when the docker compose command is executed.

It creates creates two schemas in `market_data` database, one for `stock_data` and another for `crypto_data`, and then creates tables within each schema to store `gainer`, `loser`, and `active` data for both stock and crypto.

The columns for each table are as follows:

- `id` : a unique identifier for each row in the table
- `date_collected` : the date on which the data was collected, defaulting to the current date
- `symbol` : the stock or crypto symbol
- `name` : the name of the stock or crypto
- `market_cap` : the market capitalization of the stock or crypto
- `volume` : the trading volume of the stock or crypto
- `price` : the price of the stock or crypto
- `change_percent` : the percentage change in the price of the stock or crypto

## Requirements

- [Docker](https://www.docker.com/get-started)


## Setup

1. Clone the repository: <br>

       $ git clone https://github.com/abeltavares/MarketTrackPipe.git

2. Create an '.env' file in the project's root directory with the required environment variables (refer to the example .env file in the project).

3. Start the Docker containers:<br>

       $ docker-compose up

4. Access the Airflow web server:<br>

      Go to the Airflow web UI at http://localhost:8080 and turn on the DAGs.

      Alternatively, you can trigger the DAG manually by running the following command in your terminal:

       $ airflow trigger_dag data_collection_storage_stocks
       $ airflow trigger_dag data_collection_storage_crypto
       $ airflow trigger_dag backup_data

That's it! You should now be able to collect and store stock and cryptocurrency data using MarketTrackPipe.


## Usage

After setting up the workflow, you can access the Apache Airflow web UI to monitor the status of the tasks and the overall workflow.

To access the data stored in the PostgreSQL database, you have two options:

1. Use the command-line tool `psql` to run SQL queries directly. The database credentials and connection information can be found in the '.env' file as well. Using psql, you can connect to the database, execute queries, and save the output to a file or use it as input for other scripts or applications.

       $ docker exec -it my-postgres psql -U postgres -d market_data    

2. Use `pgAdmin`, a web-based visual interface. To access it, navigate to http://localhost:5050 in your web browser and log in using the credentials defined in the `.env` file in the project root directory. From there, you can interactively browse the tables created by the pipeline, run queries, and extract the desired data for analysis or visualization.

Choose the option that suits you best depending on your familiarity with SQL and preference for a graphical or command-line interface.

## Acknowledgments 

The APIs used in this project are provided by [Alpha Vantage](https://www.alphavantage.co/documentation/), [Financial Modeling Prep](https://financialmodelingprep.com/developer/docs/), and [CoinMarketCap](https://coinmarketcap.com/api/documentation/v1/). Please refer to their documentation for more information on their APIs.


## Contributions

This project is open to contributions. If you have any suggestions or improvements, please feel free to create a pull request.

## Copyright
© 2023 Abel Tavares

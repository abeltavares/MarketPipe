[![WIP](https://img.shields.io/badge/status-Work%20In%20Progress-yellow)](https://github.com/abeltavares/stock-crypto-dashboard)
[![Powered by PostgreSQL](https://img.shields.io/badge/powered%20by-PostgreSQL-blue.svg)](https://www.postgresql.org/)
[![Python Version](https://img.shields.io/badge/python-3.x-brightgreen.svg)](https://www.python.org/downloads/)

# Stock Data Collection and Storage
This repository provides a sample workflow for collecting and storing stock data in a PostgreSQL database using Apache Airflow. The data is collected on stock gainers and can be easily adapted to collect data on other stocks such as loosers or actives.

The workflow is implemented using Python and consists of the following components:

1. data_collection_storage.py - This file contains the functions for collecting and storing stock data.

2. stock_workflow_dag.py - This file contains the definition of the DAG and its tasks in Apache Airflow.

3. conn_file.json - This file contains the configuration for connecting to the database where the stock data will be stored.


## Table of Contents

- [Getting Started](#getting-started)
- [Usage](#usage)
- [Contributions](#contributions)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Requirements

- Python 3.x
- Airflow
- PostgreSQL

### Setup
1. Clone the repository: <br>

       $ git clone https://github.com/abeltavares/python_challanges.git <br>

2. Create and activate a virtual environment: <br>

       $ python3 -m venv venv
       $ source venv/bin/activate

3. Install the dependencies:<br>

       $ pip install -r requirements.txt

4. Create the database and schema:<br>

       $ psql -f schema_tables.sql

5. Update the connection information in 'conn_file.json'<br>

       {
        "host": "localhost",
        "database": "stock_data_db",
        "user": "user",
        "password": "password",
        "schema_name": "stock_data",
         "table_name": "stocks"
       }

6. Start the Airflow web server:

       $ airflow webserver

7. Start the Airflow web server:<br>

      Go to the Airflow web UI at http://localhost:8080 and turn on the stock_data_collection DAG.

## Usage

The code will collect stock data every day at 7 PM and store the data in the PostgreSQL database. The data will be stored in the stock_data schema in the stock_data_db database.
After setting up the workflow, you can access the Apache Airflow web UI to monitor the status of the tasks and the overall workflow. You can also manually trigger the workflow or change its schedule as per your requirements.

    $ airflow trigger_dag stock_data_collection


## Contributions

This project is open to contributions. If you have any suggestions or improvements, please feel free to create a pull request.

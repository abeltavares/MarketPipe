import psycopg2
import logging
from dotenv import load_dotenv
import os

load_dotenv()


class Storage:
    """
    A class that handles storing data in a database.

    Attributes:
        logger (logging.Logger): The logger object for logging messages.
        conn: The database connection object.
        cur: The database cursor object.
    """

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.conn = None
        self.cur = None

    def _connect(self):
        try:
            self.conn = psycopg2.connect(
                host=os.getenv("POSTGRES_HOST"),
                port=os.getenv("POSTGRES_PORT"),
                database=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
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

    def store_data(self, data: dict[str, dict[str, any]], table: str) -> None:
        if not isinstance(table, str):
            error_msg = "Table name must be a string"
            self.logger.error(error_msg)
            raise TypeError(error_msg)
        try:
            self.logger.info("Storing data in the database.")

            self._connect()

            with self.conn, self.cur:
                for symbol, asset_data in data.items():
                    name = asset_data["name"]
                    volume = asset_data["volume"]
                    price = asset_data["price"]
                    market_cap = asset_data["market_cap"]
                    change_percent = asset_data["change_percent"]

                    if not all([symbol, name]):
                        self.logger.error(
                            f"One or more required fields are missing from the {table} data for symbol: {symbol}, name: {name}"
                        )
                        raise ValueError(
                            f"One or more required fields are missing from the {table} data"
                        )

                    self.cur.execute(
                        f"INSERT INTO {table} (symbol, name, market_cap, volume, price, change_percent) VALUES (%s, %s, %s, %s, %s, %s)",
                        (symbol, name, market_cap, volume, price, change_percent),
                    )

                    self.logger.info(
                        f"Successfully stored data for symbol {symbol} in the {table} table."
                    )

                self.conn.commit()

        except psycopg2.Error as error:
            self.logger.error(
                f"An error occurred while storing data in the database: {error}"
            )
            if self.conn:
                self.conn.rollback()
        finally:
            self._close()




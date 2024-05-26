import logging
from core.base_api import ApiClientFactory
from core.storage import Storage


class DataProcessor:
    def __init__(
        self,
        asset_type: str,
        api_client_factory: ApiClientFactory,
        db_connector: Storage,
        logger: logging.Logger,
    ):
        self.asset_type = asset_type
        self.api_client = api_client_factory.get_client(asset_type)
        self.logger = logger
        self.db_connector = db_connector

    def get_data(self):
        try:
            return self.api_client.get_data()
        except Exception as e:
            self.logger.error(f"Error getting {self.asset_type} data: {e}")
            raise

    def store_data(self, data):
        try:
            if data is not None:
                self.db_connector.store_data(data, self.asset_type)
                self.logger.info(
                    f"{self.asset_type.capitalize()} data stored successfully."
                )
            else:
                self.logger.warning(
                    f"No {self.asset_type} data retrieved. Nothing stored in the database."
                )
        except Exception as e:
            self.logger.error(f"Error storing {self.asset_type} data: {e}")
            raise

import logging
from core.base_api import ApiClientFactory
from core.storage import Storage

logging.basicConfig(
    level=logging.WARNING,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
)

logger = logging.getLogger(__name__)


class DataProcessor:
    def __init__(self, asset_type: str):
        self.asset_type = asset_type
        self.api_client = ApiClientFactory(logger).get_client(asset_type)
        self.db_connector = Storage(logger)

    def get_data(self):
        try:
            return self.api_client.get_data()
        except Exception as e:
            logger.error(f"Error getting {self.asset_type} data: {e}")
            raise

    def store_data(self, data):
        try:
            if data is not None:
                self.db_connector.store_data(data, self.asset_type)
                logger.info(f"{self.asset_type.capitalize()} data stored successfully.")
            else:
                logger.warning(
                    f"No {self.asset_type} data retrieved. Nothing stored in the database."
                )
        except Exception as e:
            logger.error(f"Error storing {self.asset_type} data: {e}")
            raise

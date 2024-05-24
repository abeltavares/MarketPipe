from core.base_api_client import BaseApiClient


class ApiClient(BaseApiClient):
    def __init__(self, logger):
        super().__init__(logger)

    def get_data(self) -> dict[str, dict[str, any]]:
        pass

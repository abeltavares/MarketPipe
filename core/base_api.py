import logging
from typing import Dict, Type
from importlib import import_module
from utils import read_json

CONFIG = read_json("mdp_config.json")


class BaseApiClient:
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger
        self.symbols = None

    def get_data(self):
        raise NotImplementedError("Each API client must implement this method.")


# Factory for creating API clients dynamically
class ApiClientFactory:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.clients = self.load_clients()

    @staticmethod
    def load_clients() -> Dict[str, Type[BaseApiClient]]:
        try:
            clients = {}
            for client_name, settings in CONFIG["clients"].items():
                module_name, class_name = settings["module"], settings["class"]
                module = import_module(module_name)
                clients[client_name] = getattr(module, class_name)
            return clients
        except Exception as e:
            raise Exception(f"Failed to load API clients from configuration: {e}")

    def get_client(self, client_type: str):
        client_class = self.clients.get(client_type)
        if client_class is None:
            raise ValueError(f"Invalid client type: {client_type}")

        return client_class(logger=self.logger)

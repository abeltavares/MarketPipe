import json
import sys
from unittest.mock import MagicMock


def read_json(file_path):
    print(f"Reading JSON file from {file_path}")
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


def validate_symbols(self):
    return self.symbols is not None and len(self.symbols) > 0


def mock_imports(import_list):
    """This method takes a list of imports, mocks them and adds to the system modules.

    Args:
        import_list (list): List with module names to import
    """
    for import_name in import_list:
        sys.modules[import_name] = MagicMock()


def destroy_mock_imports(import_list):
    """This method take a list of imports, and removes them from the system modules.

    Args:
        import_list (list): List with module names to remove

    Returns:
        None
    """
    sys_modules = sys.modules.copy()
    for import_name in sys_modules:
        if import_name in import_list:
            del sys.modules[import_name]

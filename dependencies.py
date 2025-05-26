import json


def get_settings() -> dict:
    return _load_data("./settings/config.json")


def get_data() -> dict:
    return _load_data("./settings/data.json")


def get_credentials() -> dict:
    return _load_data("./settings/credentials.json")


def _load_data(json_file_path: str) -> dict:
    with open(json_file_path, "r", encoding="utf-8") as jsonfile:
        data = json.load(jsonfile)
    return data
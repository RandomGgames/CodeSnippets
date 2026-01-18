"""
A module for working with configuration files.
"""

import logging
import os
import tomllib
logger = logging.getLogger(__name__)


def read_config(config_path: str) -> dict | None:
    """
    Read the configuration file from the given path, returning the parsed contents as a dictionary.
    Returns None if the file does not exist.
    """
    if not os.path.exists(config_path):
        return None

    try:
        with open(config_path, "rb", encoding="utf-8") as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        logger.error(f"Failed to parse config file '{config_path}': {e}")
        raise


def create_config(config_path: str, config: dict) -> None:
    """
    Create a new configuration file at the given path with the given contents.
    """
    try:
        with open(config_path, "w") as f:
            toml.dump(config, f)
    except Exception as e:
        raise ValueError(f"Failed to create config file '{config_path}': {e}")


def validate_config(config: dict, required_keys: dict) -> None:
    """
    Validate that the given configuration dictionary contains all of the required keys with the correct types, and does not contain any extra keys.
    Raises a ValueError if any required keys are missing, have incorrect types, or if any extra keys are present.
    """
    if not isinstance(config, dict):
        raise ValueError("Config must be a dictionary.")

    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ValueError(f"Config is missing the required key(s): {missing_keys}")

    extra_keys = [key for key in config if key not in required_keys]
    if extra_keys:
        raise ValueError(f"Config contains extra key(s) that are not required: {extra_keys}")

    for key, value_types in required_keys.items():
        if not isinstance(config[key], value_types):
            raise ValueError(f"Config value for key '{key}' must be one of {value_types}")


def load_config(config_path: str = "config.toml", create_if_not_found: bool = True) -> dict:
    """
    Load a configuration file from the given path, creating it if it doesn't exist.
    """
    logger.debug("Loading config...")

    default_config = {
        "a": "a",
        "b": 2,
        "c": ["c"],
        "d": ["d1", "d2"],
    }
    required_keys = {
        "a": (str),
        "b": (int),
        "c": (list, str),
        "d": (list, str),
    }

    config = read_config(config_path)
    if config is None:
        if create_if_not_found:
            try:
                create_config(config_path, default_config)
            except ValueError as e:
                raise ValueError(f"Failed to create config file '{config_path}': {e}")
            logger.debug("Created config file with default values.")
            config = default_config
        else:
            raise FileNotFoundError(f"Config file '{config_path}' does not exist.")

    validate_config(config, required_keys)

    logger.debug("Config loaded successfully.")
    return config


config = load_config()

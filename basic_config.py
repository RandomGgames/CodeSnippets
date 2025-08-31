import logging
import os
import toml
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.toml", create_if_not_found: bool = True) -> dict:
    logger.debug("Loading config...")

    default_config = {
        "a": "a",
        "b": 2,
        "c": ["c"],
    }
    required_keys = {"a", "b", "c"}

    if not os.path.exists(config_path):
        logger.debug(f"Config file '{config_path}' does not exist.")
        if create_if_not_found:
            logger.debug("Creating config file with default values...")
            with open(config_path, "w") as f:
                toml.dump(default_config, f)
            config = default_config
        else:
            raise FileNotFoundError(f"Config file '{config_path}' does not exist.")
    else:
        config = toml.load(config_path)

    logger.debug("Validating config...")
    if not all(key in config for key in required_keys):
        missing_keys = [key for key in required_keys if key not in config]
        raise ValueError(f"Config is missing the required key(s): {missing_keys}")
    logger.debug("Config loaded successfully.")
    return config


config = load_config()

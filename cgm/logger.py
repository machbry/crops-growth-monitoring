import logging
from logging.config import dictConfig
import yaml
from pathlib import Path


logs_conf_path = Path(__file__).parents[1] / 'conf' / 'logs.yaml'

logger_init = False


def logging_config_from_yaml(path: Path = logs_conf_path) -> dict:
    with open(path, 'r') as f:
        return yaml.safe_load(f.read())


def init_logger():
    global logger_init
    config = logging_config_from_yaml()
    dictConfig(config)
    logger_init = True


def get_logger():
    if not logger_init:
        init_logger()
    return logging.getLogger(name="cgm")

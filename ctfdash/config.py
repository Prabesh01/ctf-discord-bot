import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / '.env'
load_dotenv(ENV_FILE)

CONFIG = {}
def load_config():
    if not CONFIG:
        for key, value in os.environ.items():
            if value.isdigit(): value=int(value)
            CONFIG[key] = value
load_config()


def get_config(key, default=None):
    return CONFIG.get(key, default)

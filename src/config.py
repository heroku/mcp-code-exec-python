"""
Simple module to aggregate configuration settings.
"""
import os
from dotenv import load_dotenv

# ✅ Load environment variables from .env
load_dotenv()

def get_env_variable(var_name, required=True):
    value = os.environ.get(var_name)
    if not value and required:
        raise EnvironmentError(f"{var_name} environment variable is not set or empty.")
    return value

# ENV variables with defauls:
PORT = int(os.environ.get('PORT', 8000))
WEB_CONCURRENCY = int(os.environ.get('WEB_CONCURRENCY', 1))
STDIO_MODE_ONLY = os.getenv("STDIO_MODE_ONLY", "false").lower() == "true"
USE_TEMP_DIR = os.getenv("USE_TEMP_DIR", "false").lower() == "true"

# Local or Not:
is_one_off_dyno = os.getenv("DYNO") is not None


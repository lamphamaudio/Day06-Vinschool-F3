import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Load .env from the project root so Streamlit and scripts share one source.
load_dotenv(dotenv_path=ENV_FILE)


def get_env(name, default=""):
    value = os.getenv(name, default)
    if isinstance(value, str):
        return value.strip()
    return value

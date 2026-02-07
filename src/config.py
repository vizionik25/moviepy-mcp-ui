import os
from pathlib import Path

# Load environment variables (if python-dotenv is available, though we don't rely on it)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configuration Constants
MAX_CLIPS = int(os.environ.get("MAX_CLIPS", 100))
OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", Path.cwd() / "output"))

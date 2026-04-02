import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Base Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATCHES_DIR = os.path.join(BASE_DIR, os.getenv("MATCHES_DIR", "matches"))

# Create directories if they don't exist
if not os.path.exists(MATCHES_DIR):
    os.makedirs(MATCHES_DIR)

# Server Settings
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

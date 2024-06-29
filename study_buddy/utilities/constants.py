import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///study_buddy.db")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# time format
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT_MOMENT = "YYYY-MM-DD HH:mm:ss"
DATE_FORMAT_MOMENT = "YYYY-MM-DD"

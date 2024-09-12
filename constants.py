import os
from dotenv import load_dotenv
import telebot
from study_buddy.db import Database


# Load environment variables for the DataHub/OneLake API
load_dotenv(override=True)

# Load environment variables for the API
QDRANT_API_URL = os.getenv('QDRANT_API_URL')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
API_KEY = os.getenv('TEL_API_KEY')
bot = telebot.TeleBot(API_KEY)

# List of available commands
commands_list = """
Here are the commands you can use:

*📜 General*
- help – _Get help about the bot._

*📚 Courses*
- create course – _Create a new course._
- get courses – _List all your courses._
- delete course – _Delete a course you no longer need._

*📝 Notes*
- create note – _Upload a note (image or PDF) for a course._
- get notes – _List all your notes for a course._
- delete note – _Delete notes for a particular course._
"""

# Get the singleton instance of the database
db = Database()
# Now you can execute queries
cursor = db.get_cursor()

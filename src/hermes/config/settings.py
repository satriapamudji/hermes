import os
from dotenv import load_dotenv

# Path to directory
BASEDIR = os.path.abspath(os.path.dirname(__file__))

# Getting the variables from the .env file
load_dotenv(os.path.join(BASEDIR, '..', '..', '..', '.env'))

API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
OPENAI_MODEL = os.getenv('OPENAI_MODEL_NAME')
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
CANVAS_API_URL = os.getenv('CANVAS_API_URL', 'https://canvas.instructure.com/api/v1')
CANVAS_ACCESS_TOKEN = os.getenv('CANVAS_ACCESS_TOKEN')

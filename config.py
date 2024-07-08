import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
YOOKASSA_TEST_TOKEN = os.getenv("YOOKASSA_TEST_TOKEN")
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PATH = f"/{BOT_TOKEN}"
WEBHOOK_URI = WEBHOOK_HOST + WEBHOOK_PATH
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT"))

LOCAL_BOT_API = os.getenv('LOCAL_BOT_API')

ADMIN_ID = os.getenv("ADMIN_ID")
SUPPORT_US = os.getenv("SUPPORT_US")
BOT_USERNAME = os.getenv("BOT_USERNAME")
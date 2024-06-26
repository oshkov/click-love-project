from dotenv import load_dotenv
import os


load_dotenv()


DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOT_USERNAME = os.environ.get('BOT_USERNAME')
REFERRAL_TOKEN = os.environ.get('REFERRAL_TOKEN')
REFERRAL_IP = os.environ.get('REFERRAL_IP')
REFERRAL_PORT = os.environ.get('REFERRAL_PORT')


SUPERLIKE_PRICE = 50
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    OPENAI_API_KEY = os.getenv('KEY')

    # Google Calendar
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5000/api/calendar/callback')

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.getenv('DATA_DIR', os.path.join(BASE_DIR, 'data'))

    TASKS_FILE = 'data/tasks.json'
    CREDENTIALS_FILE = 'data/credentials.json'

    os.makedirs(DATA_DIR, exist_ok=True)

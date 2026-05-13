import os
from dotenv import load_dotenv

# Load variabel dari file .env
load_dotenv()

class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "spk_kinerja_guru")
    FONNTE_TOKEN = os.getenv("FONNTE_TOKEN", "")
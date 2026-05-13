import mysql.connector
import os
from dotenv import load_dotenv

# Ambil data dari file .env
load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT', 26190)), # Tambahkan port karena Aiven pakai 26190
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
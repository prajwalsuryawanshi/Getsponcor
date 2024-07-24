import os

TEMP_DIR = '/tmp'  # Vercel's writable temporary directory
DATABASE_FILE = 'database.db'
SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(TEMP_DIR, DATABASE_FILE)}'

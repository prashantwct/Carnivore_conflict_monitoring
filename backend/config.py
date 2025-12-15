import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration settings loaded from environment variables."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-highly-secret-key-that-must-be-changed'

    # Database Configuration (PostgreSQL/PostGIS)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Recommended to be False

    # Cloud Storage Configuration (Example for AWS S3)
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_BUCKET_NAME = os.environ.get('AWS_BUCKET_NAME')
    
    if not SQLALCHEMY_DATABASE_URI:
        print("WARNING: DATABASE_URL not set. Set it in the .env file.")

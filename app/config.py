import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///chat_with_voice.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'voice_messages'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB file upload limit

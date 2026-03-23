import os

class Config:
    SECRET_KEY = 'keyword_based_search_engine'

    # Database
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///../database/app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, '../data/uploads')

    # Whoosh Index
    WHOOSH_INDEX = os.path.join(BASE_DIR, '../data/index')
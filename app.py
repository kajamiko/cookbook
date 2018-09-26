from flask import Flask
from flask_pymongo import PyMongo
import os

UP_FOLDER = 'static/uploaded_images/'
def create_app():
    
    application = Flask(__name__)
    application.config.update(
    MONGO_DBNAME= os.environ.get('MONGO_DB'),
    MONGO_URI = os.environ.get('MONGODB'),
    SECRET_KEY = str(os.environ.get('SECRET_KEY')),
    UPLOAD_FOLDER = UP_FOLDER
    )
    
    return application


app = create_app()

mongo = PyMongo(app)

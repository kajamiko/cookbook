from flask import Flask
import os
from flask_pymongo import PyMongo

UP_FOLDER = 'static/uploaded_images/'
# def create_app():
    
#     application = 
#     application.config.update(
#     MONGO_DBNAME= os.environ.get('MONGO_DB'),
#     MONGO_URI = os.environ.get('MONGODB'),
#     SECRET_KEY = str(os.environ.get('SECRET_KEY')),
#     UPLOAD_FOLDER = UP_FOLDER
#     )
    
#     return application


app = Flask(__name__)
app.config.update(
    MONGO_DBNAME= os.environ.get('MONGO_DB'),
    MONGO_URI = os.environ.get('MONGODB'),
    SECRET_KEY = str(os.environ.get('SECRET_KEY')),
    UPLOAD_FOLDER = UP_FOLDER
    )
mongo = PyMongo(app)


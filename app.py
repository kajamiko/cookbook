from flask import Flask
from flask_pymongo import PyMongo

UP_FOLDER = 'static/uploaded_images/'
def create_app(conf_obj):
    
    application = Flask(__name__)
    application.config.from_object(conf_obj)
    
    return application


app = create_app(conf_obj='conf.Config')
app.config['UPLOAD_FOLDER'] = UP_FOLDER

mongo = PyMongo(app)


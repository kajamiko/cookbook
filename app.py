from flask import Flask
from flask_pymongo import PyMongo


UP_FOLDER = 'static/uploaded_images/'
def create_app(conf_obj='conf.TestingConfig'):
    
    application = Flask(__name__)
    application.config.from_object(conf_obj)
    
    return application
# setting up configuration
#('Config')

app = create_app(conf_obj='conf.Config')
app.config['UPLOAD_FOLDER'] = UP_FOLDER
mongo = PyMongo(app)


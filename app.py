from flask import Flask
from flask_pymongo import PyMongo
from basic import UP_FOLDER
from secret import secret_key



def create_app(conf_obj='conf.TestingConfig'):
    
    application = Flask(__name__)
    application.config.from_object(conf_obj)
    application.secret_key = secret_key
    return application
# setting up configuration
#('Config')
app = create_app(conf_obj='conf.Config')
mongo = PyMongo(app)


import os
from flask import Flask, render_template, redirect, request, url_for
import pymongo
from flask_pymongo import PyMongo
from secret import db_name, uri_str
import datetime




app = Flask(__name__)
app.config["MONGO_DBNAME"] = db_name
app.config["MONGO_URI"] = uri_str

mongo = PyMongo(app)


def create_nice_date():
    now = datetime.datetime.now()
    new_date = "{0}-{1}-{2}".format(now.day,now.month,now.year)
    return new_date

def say_hello():
    return "hello"
    
def homepage(query={}):
    
    return mongo.db.recipes.find(query)




if __name__ == "__main__":
    app.run(host=os.environ.get('IP'),
    port=int(os.environ.get('PORT')),
    debug=True)
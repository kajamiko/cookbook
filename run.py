import os
from flask import Flask, render_template, redirect, request, url_for
import pymongo
from bson.objectid import ObjectId
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

def create_cookbook(cookbook_name='', password='', username=''):
    """
    """
    _id=mongo.db.cookbooks.insert_one({"cookbok_name": cookbook_name,
        "password" : password,
        "author_name": username,
        "created_on": create_nice_date(),
        "recipes_pinned": [],
        "recipes_owned": []
    })
    
    return _id

def say_hello():
    return "hello"
    
def get_recipes(query={}):
    
    return mongo.db.recipes.find(query)


def get_cookbooks(query={}):
    return mongo.db.cookbooks.find_one(query)


if __name__ == "__main__":
    app.run(host=os.environ.get('IP'),
    port=int(os.environ.get('PORT')),
    debug=True)
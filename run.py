import os
from flask import Flask, render_template, redirect, request, url_for, flash
import pymongo
from bson.objectid import ObjectId
from flask_pymongo import PyMongo
from secret import db_name, uri_str, secret_key
import datetime


app = Flask(__name__)
app.config["MONGO_DBNAME"] = db_name
app.config["MONGO_URI"] = uri_str
app.secret_key = secret_key

mongo = PyMongo(app)

### Raw functions ###

def create_nice_date():
    """
    Returns current date in dd-mm-yyyy format
    """
    now = datetime.datetime.now()
    new_date = "{0}-{1}-{2}".format(now.day,now.month,now.year)
    return new_date

def create_cookbook(cookbook_name='', password='', username='', description=''):
    """
    Inserts given parameters as a cookbook document and returns its id 
    """
    _id=mongo.db.cookbooks.insert_one({"cookbok_name": cookbook_name,
        "password" : password,
        "author_name": username,
        "cookbook_desc": description,
        "created_on": create_nice_date(),
        "recipes_pinned": [],
        "recipes_owned": []
    })
    return _id

def get_recipes(query={}):
    return mongo.db.recipes.find(query)

def get_cookbooks(query={}):
    return mongo.db.cookbooks.find_one(query)

              

### Front end making functions

@app.route('/', methods=["GET", "POST"])
def register():
    if(request.method == "POST"):
        
            
        form = request.form 
            
        create_cookbook(cookbook_name=form["cookbook_name"],
            password=form["password"],
            username=form["author_name"], 
            description=form["cookbook_desc"])
               

    return render_template('register.html')

if __name__ == "__main__":
    app.run(host=os.environ.get('IP'),
    port=int(os.environ.get('PORT')),
    debug=True)
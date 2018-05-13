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
    Inserts given parameters as a cookbook document to the db and returns it's id 
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

def get_record(collection, query={}):
    return collection.find_one(query)

def delete_record(record_id):
    
    pass


### Front end making functions

@app.route('/', methods=["GET", "POST"])
def register():
    if(request.method == "POST"):
        
        form = request.form 
            
        _result=create_cookbook(cookbook_name=form["cookbook_name"],
            password=form["password"],
            username=form["author_name"], 
            description=form["cookbook_desc"])
              
        return redirect(url_for('cookbook_view', cookbook_id=_result.inserted_id))
    return render_template('register.html')

####Started coookbook view, but need to implement html view

@app.route('/cookbook_view/<cookbook_id>')
def cookbook_view(cookbook_id):
    _cookbook = mongo.db.cookbooks.find_one({"_id": cookbook_id})
    return render_template('cookbook_view.html',
    cookbook=_cookbook)
    

    
@app.route('/show_recipe/<recipe_id>')
def show_recipe(recipe_id):
     _recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
     
     return render_template("recipe.html",
     recipe=_recipe )
     

@app.route('/give_up/<recipe_id>')
def give_up(recipe_id):
    _recipe = mongo.db.recipes.update_one({"_id": ObjectId(recipe_id)},
        {'$inc': {"upvotes" : 1}})
    return redirect(url_for("show_recipe",recipe_id=recipe_id))

if __name__ == "__main__":
    app.run(host=os.environ.get('IP'),
    port=int(os.environ.get('PORT')),
    debug=True)
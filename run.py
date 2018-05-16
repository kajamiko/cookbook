import os
from flask import Flask, render_template, redirect, request, url_for, flash, session
import pymongo
from bson.objectid import ObjectId
from flask_pymongo import PyMongo
from secret import db_name, uri_str, secret_key
import datetime
import re
from flask import Blueprint
from flask_paginate import Pagination, get_page_parameter


app = Flask(__name__)
app.config["MONGO_DBNAME"] = db_name
app.config["MONGO_URI"] = uri_str
app.secret_key = secret_key

mongo = PyMongo(app)

### Raw functions ###

    
def check_if_exists(field, value):
 
    return mongo.db.cookbooks.find_one({field: value})

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
    _id = ""
    if(check_if_exists("author_name", username) == check_if_exists("cookbook_name", cookbook_name)):
        _id=mongo.db.cookbooks.insert_one({"cookbook_name": cookbook_name,
            "password" : password,
            "author_name": username,
            "cookbook_desc": description,
            "created_on": create_nice_date(),
            "recipes_pinned": [],
            "recipes_owned": []
        })
        return _id
    else:
        return "Error! Some value already exists"


def get_record(collection, query={}):
    return collection.find_one(query)

def delete_record(record_id):
    
    pass


def exclude_query(ready_string):
    """
    gets strings into find query, converts to regexp?
    """
    return mongo.db.recipes.find({"ingredients_list": {'$not': re.compile(ready_string, re.I)}})


### Front end making functions


@app.route('/', methods=["GET","POST"])
@app.route('/get_recipes', methods=["GET","POST"])
@app.route('/cuisines/<cuisine_name>')
@app.route('/dishes/<dish_name>')
@app.route('/filter', methods=["GET","POST"])
def get_recipes(cuisine_name="", dish_name="", query=""):
    """This function takes optional arguments to pass a query to the database, or if none, it just gets all the recipes
    """
    username = session.get('username')
    #return 'Logged in as ' + username + '<br>' + \
    query_db = ""
    if (query):
        query_db = {"$text": {"$search": query }}
    page = request.args.get(get_page_parameter(), type=int, default=1)
    
    allergens = ""
    if(cuisine_name):
        recipes = mongo.db.recipes.find({"cuisine_name": cuisine_name})

    elif(dish_name):
        recipes = mongo.db.recipes.find({"dish_type": dish_name})
    else:
        
        if (request.method == "POST"):
            str_allergens = ""
            for k,v in request.form.to_dict().items():
                if(k):
                    
                    temp = str_allergens
                    str_allergens = temp + v 
                    allergens = str_allergens.replace(' ', '|')
            
            recipes = exclude_query(allergens)
        else:
            if(query_db != ""):
                recipes = mongo.db.recipes.find(query_db)
            else:
                recipes = mongo.db.recipes.find() 
            
    recipes.sort('upvotes', pymongo.DESCENDING)
    pagination = Pagination(page=page, total=recipes.count(),
    record_name='recipes',per_page=5,
    css_framework="bootstrap4")
    
    return render_template("recipes.html",
        recipes=recipes,
        pagination=pagination,
        username = username)

@app.route('/register', methods=["GET", "POST"])
def register():
    message = ""
    if(request.method == "POST"):
        form = request.form 
        _result=create_cookbook(cookbook_name=form["cookbook_name"],
            password=form["password"],
            username=form["author_name"], 
            description=form["cookbook_desc"])
              
        if _result != "Error":
            return redirect(url_for('cookbook_view', cookbook_id=_result.inserted_id))
        else:
            message = _result
    return render_template('register.html', message = message)

####Started coookbook view, but need to implement html view

@app.route('/cookbook_view/<cookbook_id>')
def cookbook_view(cookbook_id):
    _cookbook = mongo.db.cookbooks.find_one({"_id": ObjectId(cookbook_id)})
    
    return render_template('cookbook_view.html',
    cookbook=_cookbook,
    username =session.get('username'))
    
    
@app.route('/show_recipe/<recipe_id>')
def show_recipe(recipe_id):
     _recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
     
     return render_template("recipe.html",
     recipe=_recipe,
     username =session.get('username'))
     

@app.route('/give_up/<recipe_id>')
def give_up(recipe_id):
    _recipe = mongo.db.recipes.update_one({"_id": ObjectId(recipe_id)},
        {'$inc': {"upvotes" : 1}})
    return redirect(url_for("show_recipe",recipe_id=recipe_id))


@app.route('/add_recipe')
def add_recipe():
    
    return render_template("add_recipe.html",
    dishes=mongo.db.dishes.find(),
    cuisine_list=mongo.db.cuisines.find(),
    username=session.get('username'))
    
@app.route('/insert_recipe', methods=['POST'])
def insert_recipe(username=""):
    recipes = mongo.db.recipes
    # creating an empty dictionary to send it later as a new document, to the database. 
    request_ready = {}
    if( request.method == "POST"):
        new_date = create_nice_date()
        """
         filling disctionary with data from the form, with large strings sliced to an array
         and pushing and popping out some data
        """
        for k, v in request.form.to_dict().items():
            if ( k== "ingredients_list"):
                request_ready.setdefault(k,v.splitlines())
            elif ( k== "preparation_steps_list"):
                request_ready.setdefault(k,v.splitlines())
            else: 
                request_ready[k]=v
        if(request_ready["cuisine_name"] == ""):
            del request_ready["cuisine_name"] 
        # and adding some other initial data
        request_ready.setdefault("upvotes", 0)
        request_ready.setdefault("views", 0)
        request_ready.setdefault("created_on", new_date)
        if (username):
            mongo.db.cookbooks.find_one_and_update("") 
        
        recipes.insert_one(request_ready)
    return redirect(url_for('get_recipes', username = session.get('username')))  
  

    
@app.route('/category_view/<collection_name>')
def category_view(collection_name):
    if(collection_name == "cuisines"):
        return render_template('category_view.html',
        dataset = mongo.db.cuisines.find(),
        cuisines = True)
    elif(collection_name == "dishes"):
        return render_template('category_view.html',
        dataset = mongo.db.dishes.find(),
        dishes = True,
        username = session.get('username'))
    
@app.route('/login', methods = ['GET', 'POST'])
def login():
    message=""
    if (request.method == 'POST'):
        form = request.form
        doc = mongo.db.cookbooks.find_one({"author_name": form["author_name"]})
        print(doc)
        if (doc): # if exists in db
            if(form["password"] == doc["password"]): # if password correct
                session['username'] = form['author_name']
                return redirect(url_for('cookbook_view', cookbook_id = doc["_id"]))
            else: # and if password is not correct
                message = "Incorrect password"
        else:# if not exist
            message = "User does not exist"
        
     
    return render_template('login.html', message=message)
      
@app.route('/your_cookbook/<username>')
def your_cookbook(username):
    
    _cookbook = mongo.db.cookbooks.find_one({"author_name": session.get('username')})
    return redirect(url_for('cookbook_view', 
    cookbook_id = _cookbook["_id"],
    username = session.get('username')))
    
     
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('get_recipes'))
    
    
if __name__ == "__main__":
    app.run(host=os.environ.get('IP'),
    port=int(os.environ.get('PORT')),
    debug=True)
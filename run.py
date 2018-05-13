import os
from flask import Flask, render_template, redirect, request, url_for, flash
import pymongo
from bson.objectid import ObjectId
from flask_pymongo import PyMongo
from secret import db_name, uri_str, secret_key
import datetime
import re


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
    
    
"""
def get_recipes(query={}):
    return mongo.db.recipes.find(query)
"""
def get_record(collection, query={}):
    return collection.find_one(query)

def delete_record(record_id):
    
    pass
def pass_query(ready_string):
    """
    gets strings into find query, converts to regexp?
    """
    return mongo.db.recipes.find({"ingredients_list": {'$not': re.compile(ready_string, re.I)}})

### Front end making functions


@app.route('/', methods=["GET","POST"])
@app.route('/get_recipes')
@app.route('/cuisines/<cuisine_name>')
@app.route('/dishes/<dish_name>')
@app.route('/filter', methods=["GET","POST"])
def get_recipes(cuisine_name="", dish_name="", query={}):
    """This function takes optional arguments to pass a query to the database, or if none, it just gets all the recipes
    """
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
            
            print(allergens)
            recipes = pass_query(allergens)
            
        else:
            
            recipes = mongo.db.recipes.find()
            
            
    recipes.sort('upvotes', pymongo.DESCENDING)
    
    return render_template("recipes.html",
    recipes=recipes)

@app.route('/register', methods=["GET", "POST"])
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


@app.route('/add_recipe')
def add_recipe():
    
    return render_template("add_recipe.html",
    dishes=mongo.db.dishes.find(),
    cuisine_list=mongo.db.cuisines.find())
    
@app.route('/insert_recipe', methods=['POST'])
def insert_recipe():
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
        
        
        recipes.insert_one(request_ready)
    return redirect(url_for('get_recipes'))  
  

@app.route('/cuisines')
def cuisines():

    return render_template('category_view.html',
    dataset = mongo.db.cuisines.find(),
    cuisines = True)
    
@app.route('/dishes')
def dishes():
     return render_template('category_view.html',
    dataset = mongo.db.dishes.find(),
    dishes = True)


if __name__ == "__main__":
    app.run(host=os.environ.get('IP'),
    port=int(os.environ.get('PORT')),
    debug=True)
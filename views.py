from flask import Flask, render_template, redirect, request, url_for, flash, session
import pymongo
from werkzeug.utils import secure_filename
import datetime
from bson.objectid import ObjectId
from flask_pymongo import PyMongo
from conf import db_name, uri_str, UP_FOLDER, secret_key
import os
import re
from math import ceil
from flask import Blueprint
from flask_paginate import Pagination, get_page_parameter


PER_PAGE = 5


def create_app(conf_obj='conf.TestingConfig'):
    
    application = Flask(__name__)
    application.config.from_object(conf_obj)
    application.secret_key = secret_key
    return application

# setting up configuration
#('Config')
app = create_app(conf_obj='conf.Config')
mongo = PyMongo(app)



ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_if_exists(field, value):
 
    return mongo.db.cookbooks.find_one({field: value})


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



def exclude_query(ready_string):
    """
    passes strings into find query, converts to regexp
    """
    return mongo.db.recipes.find({"ingredients_list": {'$not': re.compile(ready_string, re.I)}})


def update_recipes_array(recipe_id, recipe_title="", type_of_array='recipes_pinned', remove = False):
    if(remove == False):
        return mongo.db.cookbooks.update({'author_name': session.get('username')}, 
                { '$push': 
                    { type_of_array: 
                        {'_id': recipe_id, 'title': recipe_title}
                        
                    }}
                    )
    else:
        return  mongo.db.cookbooks.update({'author_name': session.get('username')}, 
                { '$pull': 
                    { type_of_array: 
                        {'_id': recipe_id}
                        
                    }}
                    )
    


def create_nice_date():
    """
    Returns current date in dd-mm-yyyy format
    """
    now = datetime.datetime.now()
    new_date = "{0}-{1}-{2}".format(now.day,now.month,now.year)
    return new_date
    
@app.route('/', methods=["GET","POST"])
@app.route('/get_recipes', methods=["GET","POST"])
@app.route('/cuisines/<cuisine_name>')
@app.route('/dishes/<dish_name>')
@app.route('/filter', methods=["GET","POST"])
def get_recipes(cuisine_name="", dish_name="", query=""):
    """This function takes optional arguments to pass a query to the database, or if none, it just gets all the recipes
    """
    #menu = []
   # menu = mongo.db.recipes.aggregate({ "$sample": { "size": 1 } })
   
    query_db = ""
    if (query):
        query_db = {"$text": {"$search": query }}
    
    page = request.args.get(get_page_parameter(), type=int, default=1)
    allergens = ""
    if(cuisine_name):
        recipes = mongo.db.recipes.find({"cuisine_name": cuisine_name}).skip(PER_PAGE * (page-1)).limit(PER_PAGE)
        
    elif(dish_name):
        recipes = mongo.db.recipes.find({"dish_type": dish_name}).skip(PER_PAGE * (page-1)).limit(PER_PAGE)
    else:
        
        if (request.method == "POST"):
            str_allergens = ""
            for k,v in request.form.to_dict().items():
                if(k):
                    
                    temp = str_allergens
                    str_allergens = temp + v 
                    allergens = str_allergens.replace(' ', '|')
            
            recipes = exclude_query(allergens)
            recipes.skip(PER_PAGE * (page-1)).limit(PER_PAGE)
        else:
            if(query_db != ""):
                recipes = mongo.db.recipes.find(query_db).skip(PER_PAGE * (page-1)).limit(PER_PAGE)
            else:
                recipes = mongo.db.recipes.find().skip(PER_PAGE * (page-1)).limit(PER_PAGE)
            
    
    recipes.sort('upvotes', pymongo.DESCENDING)
    
    pagination = Pagination(page=page, total=recipes.count(), per_page=PER_PAGE,
                record_name='recipes', bs_version=4)
      
    return render_template("recipes.html",
        pagination = pagination,
        recipes=recipes)

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



@app.route('/cookbook_view/<cookbook_id>')
def cookbook_view(cookbook_id):
    _cookbook = mongo.db.cookbooks.find_one({"_id": ObjectId(cookbook_id)})
    
    return render_template('cookbook_view.html',
    cookbook=_cookbook)
    
    
@app.route('/show_recipe/<recipe_id>')
def show_recipe(recipe_id):
    
    already_got = False
    owned = False
    _recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    if("logged_in" in session):
        if (mongo.db.cookbooks.find_one({"author_name": session.get('username'), "recipes_pinned._id" : ObjectId(recipe_id)})):
             already_got = True
             
        elif (mongo.db.cookbooks.find_one({"author_name": session.get('username'), "recipes_owned._id" : ObjectId(recipe_id)})):
            already_got = True
            owned = True
            
    return render_template("recipe.html",
    recipe=_recipe,
    already_got=already_got,
    owned = owned)
     

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
    #username=session.get('username'))
    
@app.route('/insert_recipe', methods=['POST'])
def insert_recipe():
    recipes = mongo.db.recipes
    # creating an empty dictionary to send it later as a new document, to the database. 
    request_ready = {}
    if( request.method == "POST"):
        username = session.get('username')
        new_date = create_nice_date()
        file = request.files['file']
        """
         filling disctionary with data from the form, with large strings sliced to an array
         and pushing and popping out some data
        """
# empty image file will be prevented with js form validation
        if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # get me a full pathname and save the file
                file_path = "uploaded_images/" + filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
                flash("Incorrent file extension. Allowed extensions: png, jpg, jpeg or gif")
        
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
        request_ready.setdefault("author_name", username)
        request_ready.setdefault("image_url", file_path)
        #push everything to the database and store returned data in _result
        _result = recipes.insert_one(request_ready)
        print(request_ready)
        if (username):
            # push to owned by username
            
            update_recipes_array(ObjectId(_result.inserted_id), request_ready['recipe_name'], type_of_array='recipes_owned')
          
            
            """
            value = request_ready['recipe_name']
            mongo.db.cookbooks.update({'author_name': username}, 
            { '$push': 
                {'recipes_owned': 
                    {'_id': ObjectId(_result.inserted_id), 'title': value}
                    
                }}
                )"""
    return redirect(url_for('get_recipes'))  
  

    
@app.route('/category_view/<collection_name>')
def category_view(collection_name):
    if(collection_name == "cuisines"):
        return render_template('category_view.html',
        dataset = mongo.db.cuisines.find(),
        cuisines = True)
    elif(collection_name == "dishes"):
        return render_template('category_view.html',
        dataset = mongo.db.dishes.find(),
        dishes = True)
        #username = session.get('username'))
    
@app.route('/login', methods = ['GET', 'POST'])
def login():
    message=""
    if (request.method == 'POST'):
        form = request.form
        doc = mongo.db.cookbooks.find_one({"author_name": form["author_name"]})
        if (doc): # if exists in db
            if(form["password"] == doc["password"]): # if password correct
                session['username'] = doc["author_name"]
                session['logged_in'] = True
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
    cookbook_id = _cookbook["_id"]))
    
@app.route('/logout')
def logout():

    session.clear()
    print (session.get('username'))
    return redirect(url_for('get_recipes'))
    
@app.route('/pin_recipe/<recipe_id>/<recipe_title>')
def pin_recipe(recipe_id, recipe_title):
    update_recipes_array(ObjectId(recipe_id), recipe_title = recipe_title)
    return redirect(url_for('show_recipe', recipe_id=recipe_id))
    

@app.route('/remove_recipe/<recipe_id>')
def remove_recipe(recipe_id, owned=False):
    print("Is it owned? ", owned)
    if(owned):
        print("Removing!")
        mongo.db.recipes.delete_one({"_id": ObjectId(recipe_id)})
        update_recipes_array(ObjectId(recipe_id), type_of_array="recipes_owned", remove = True)
    else:
        update_recipes_array(ObjectId(recipe_id), remove = True)
    return redirect(url_for('show_recipe', recipe_id=recipe_id))
    
@app.route('/summarise', methods = ['GET','POST'])
def summarise(what_to_check="author_name", chart_type="'doughnut'"):
    
    """
    This function queries database and keeps data in arrays that are passed to a javascript file
    """
    datanames = []
    dataset = []
    if( request.method == 'POST'):
        chart_type = request.form['chart_type']
        what_to_check = request.form['what_to_check']
        print(chart_type)

    recipes = mongo.db.recipes.find()
    for recipe in recipes:
        if (what_to_check in recipe):
            name = recipe[what_to_check]
            if (name not in datanames):
                datanames.append(name)
                dataset.append(mongo.db.recipes.find({what_to_check: name}).count())
    # this checks if a field doesnt exist, especially cuisine type, can be then labeled as none
    count = mongo.db.recipes.find({ what_to_check: {"$exists": False}}).count()
    if(count != 0 ):
        dataset.append(count)
        datanames.append("None")
    if(what_to_check == "author_name"):
        dataset = dataset[:4]
        datanames = datanames[:4]
        
    return render_template("plot.html", 
    dataset = dataset,
    datanames = datanames,
    chart_type=chart_type)

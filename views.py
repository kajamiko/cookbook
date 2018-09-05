from flask import Flask, render_template, redirect, request, url_for, flash, session
import pymongo
from bson.objectid import ObjectId
from conf import db_name, uri_str, UP_FOLDER
from secret import secret_key
from app import app, mongo
from werkzeug.utils import secure_filename
import os
import re
from math import ceil
from flask import Blueprint
from basic import allowed_file, PER_PAGE, check_if_exists, get_record, create_cookbook, exclude_query, update_recipes_array, create_nice_date
from flask_paginate import Pagination, get_page_parameter

 
   
@app.route('/', methods=["GET","POST"])
def index():
    """
    Homepage view function : getting random recipes from selected categories
    """
    dinner = mongo.db.recipes.aggregate([{"$match": {"dish_type": "Sides"}},{ "$sample": { "size": 1 }}])
    main = mongo.db.recipes.aggregate([{"$match": {"dish_type": "Main"}},{ "$sample": { "size": 1 }}])
    dessert = mongo.db.recipes.aggregate([{"$match": {"dish_type": "Desserts"}},{ "$sample": { "size": 1 }}])
    breakfast = mongo.db.recipes.aggregate([{"$match": {"dish_type": "Breakfast"}},{ "$sample": { "size": 1 }}])
    return render_template('index.html', 
                            dinner=dinner, 
                            main=main,
                            dessert=dessert, 
                            breakfast=breakfast)

@app.route('/get_recipes', methods=["GET","POST"])
@app.route('/cuisines/<cuisine_name>')
@app.route('/dishes/<dish_name>')
def get_recipes(cuisine_name="", dish_name=""):
    """
    This function:
    1. Takes optional arguments: 'dishes' or 'cuisines' to filter recipes by categories.
    2. Returns all recipes or filtered recipes, as it processes form allowing to filter allergens and/or search by keyword.
    3. Supports results pagination.
    """
    
    page = request.args.get(get_page_parameter(), type=int, default=1)
    
    if(cuisine_name):
        recipes = mongo.db.recipes.find({"cuisine_name": cuisine_name}).skip(PER_PAGE * (page-1)).limit(PER_PAGE)
        
    elif(dish_name):
            
        recipes = mongo.db.recipes.find({"dish_type": dish_name}).skip(PER_PAGE * (page-1)).limit(PER_PAGE)
    else:
        recipes = mongo.db.recipes.find().skip(PER_PAGE * (page-1)).limit(PER_PAGE)
            
    recipes.sort('upvotes', pymongo.DESCENDING)
    
    pagination = Pagination(page=page, total=recipes.count(), per_page=PER_PAGE,
                record_name='recipes', bs_version=4)
    # flash a message if there was no result
    if recipes.count()==0:
        flash("We found no results for your filters...try different ones")
    return render_template("recipes.html",
                pagination = pagination,
                recipes=recipes,
                cuisines=mongo.db.cuisines.find(),
                dishes=mongo.db.dishes.find())   
        

@app.route('/filter', methods=["GET", "POST"])
def filter_query():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    cuisines=mongo.db.cuisines.find()
    dishes=mongo.db.dishes.find()
    
    if (request.method == "POST"):
        query_db, recipes = {}, {}
        # str_allergens = request.args.get('str_allergens')
        and_list, or_dish_list, or_cuisine_list = [], [], []
        request_ready = request.form.to_dict()
        query = request.form["query"]
        #make sure query string will not get into allergens list
        del request_ready["query"]
        # setting values for filter and exclde
        temp_list = []
        # here the code is iterating through cursors to get names, and then iterating through form dictionary to check if there are any values
        # coresponding, and then adding to separate lists to later send $or query, and deleting from request_ready to later pass to strig processing
        for cuisine in cuisines:
            temp_list.append(cuisine["name"])
        for k,v in request.form.to_dict().items():
            if k in temp_list:
                or_cuisine_list.append({"cuisine_name": v})
                del request_ready[k]
        temp_list.clear()
        for dish in dishes:
            temp_list.append(dish["name"])
        for k,v in request.form.to_dict().items():
            if k in temp_list:
                or_dish_list.append({"dish_type": v})
                del request_ready[k]
        print(or_dish_list)
        str_allergens = exclude_query(request_ready)
        print("The processed string is {0}".format(str_allergens))
        # setting documents for each
        # if query or str_allergens:
        #     return redirect(url_for('filter_query', query=query, str_allergens=str_allergens, dish_name=dish_name, cuisine_name=cuisine_name))
        
        # if there are some allergens to and keyword
        if (str_allergens!="" and query!=""):
            # search_allergens = {"ingredients_list": {'$not': re.compile(str_allergens, re.I)}}
            print(str_allergens)
            look_for_words = query + str_allergens
            search_text = {"$text": {"$search": look_for_words }}
            and_list.append(search_text)
        # if there is some keyword but no allergens
        elif (str_allergens=="" and query!=""):
            search_text = {"$text": {"$search": query }}
            and_list.append(search_text)
        # no query, allergens only
        elif (str_allergens!="" and query==""):
            no_query_allergens = "1" + str_allergens
            search_text = {"$text": {"$search": no_query_allergens }}
            and_list.append(search_text)
            
        if (len(or_cuisine_list) > 1):
            and_list.append({"$or": or_cuisine_list})
        elif (len(or_cuisine_list) == 1):
            and_list.append(or_cuisine_list[0])
        
        if (len(or_dish_list) > 1):
            and_list.append({"$or": or_dish_list})
        elif (len(or_dish_list) == 1):
            and_list.append(or_dish_list[0])
            
        if (len(and_list) > 1):
            query_db = {"$and": and_list}
        elif (len(and_list) == 1):
            query_db = and_list[0]
            
        elif str_allergens== "" and query=="":
                return redirect(url_for('get_recipes')) 
        
        session['query'] = query_db
        print("I'm sesion")
        print(session['query'])
        recipes = mongo.db.recipes.find(query_db).skip(PER_PAGE * (page-1)).limit(PER_PAGE)
        if recipes.count()==0:
            flash("We found no results for your filters...try different ones")
        return redirect(url_for('filter_query'))
    else:
        
        query_db = session['query']
        recipes = mongo.db.recipes.find(query_db).skip(PER_PAGE * (page-1)).limit(PER_PAGE)
        if recipes.count()==0:
            flash("We found no results for your filters...try different ones")
        pagination = Pagination(page=page, total=recipes.count(), per_page=PER_PAGE,
                record_name='recipes', bs_version=4)
        return render_template("recipes.html",
                            pagination = pagination,
                            recipes = recipes,
                            cuisines=mongo.db.cuisines.find(),
                            dishes=mongo.db.dishes.find()
                            )

@app.route('/cancel_search')
def cancel_search():
    session.pop('query')
    return redirect(url_for('get_recipes'))
    
############ Creating cookbook/ cookbook views logic ############################################ 

@app.route('/register', methods=["GET", "POST"])
def register():
    """
    Displays form and after POST request, calls a function creating a new cookbook document.
    """
    message = ""
    if(request.method == "POST"):
        form = request.form 
        if(len(form["cookbook_name"]) >= 4 and len(form["password"]) > 5 and len(form["author_name"])>=3):
            _result=create_cookbook(cookbook_name=form["cookbook_name"],
                password=form["password"],
                username=form["author_name"], 
                description=form["cookbook_desc"])
                
            if _result != "Error! Username or cookbook's title already exists":
                session['username'] = form["author_name"]
                session['logged_in'] = True
                flash("Congratulatons! Here's your new and shiny cookbook.")
                return redirect(url_for('cookbook_view', cookbook_id=_result.inserted_id))
            else:
                message = _result
        else:
            message = "Some of your details were incorrect"
              
        
    return render_template('register.html', message = message)



@app.route('/cookbook_view/<cookbook_id>')
def cookbook_view(cookbook_id):
    _cookbook = mongo.db.cookbooks.find_one({"_id": ObjectId(cookbook_id)})
    
    return render_template('cookbook_view.html',
    cookbook=_cookbook)
  
@app.route('/your_cookbook/<username>')
def your_cookbook(username):
    """
    Redirects to a cookbook view
    """
    _cookbook = mongo.db.cookbooks.find_one({"author_name": session.get('username')})
    return redirect(url_for('cookbook_view', 
    cookbook_id = _cookbook["_id"]))

########################## Adding/showing recipes logic ############################################################3    
    
@app.route('/show_recipe/<recipe_id>')
def show_recipe(recipe_id):
    """
    Shows recipe page, which contain details and links to upvote it.
    """
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

@app.route('/edit_recipe/<recipe_id>/<owned>')
def edit_recipe(recipe_id, owned):
    # if(owned == "False"):
    _recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    
    return render_template('recipe_edit.html',
            recipe = _recipe,
            dishes=mongo.db.dishes.find(),
            cuisine_list=mongo.db.cuisines.find())

@app.route('/add_recipe')
def add_recipe():
    """
    """
    return render_template("add_recipe.html",
    dishes=mongo.db.dishes.find(),
    cuisine_list=mongo.db.cuisines.find())
    
@app.route('/insert_recipe', methods=['POST'])
def insert_recipe():
    recipes = mongo.db.recipes
    # creating an empty dictionary to send it later as a new document, to the database. 
    request_ready = {}
    if( request.method == "POST"):
        form = request.form
        if len(form["recipe_name"])>4 and len(form["ingredients_list"])>10 and len(form["preparation_steps_list"])>10:
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
                # push to owned
                update_recipes_array(ObjectId(_result.inserted_id), request_ready['recipe_name'], type_of_array='recipes_owned')
            
        else:
            flash("Some of your values were incorrent.")
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

############### Login/logout logic ################################################
    
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
    
    
@app.route('/logout')
def logout():
    """
    Logging out logic
    """
    session.clear()
    print (session.get('username'))
    return redirect(url_for('get_recipes'))    
    

############## Pinning/removing/ upvoting recipes logic
@app.route('/pin_recipe/<recipe_id>/<recipe_title>')
def pin_recipe(recipe_id, recipe_title):
    update_recipes_array(ObjectId(recipe_id), recipe_title = recipe_title)
    return redirect(url_for('show_recipe', recipe_id=recipe_id))
   
@app.route('/remove_recipe/<recipe_id>/<owned>')
def remove_recipe(recipe_id, owned):
    if(owned == "False"):
        update_recipes_array(ObjectId(recipe_id), remove = True)
        return redirect(url_for('show_recipe', recipe_id=recipe_id))
       
    else:
        mongo.db.recipes.delete_one({"_id": ObjectId(recipe_id)})
        update_recipes_array(ObjectId(recipe_id), type_of_array="recipes_owned", remove = True)
        return redirect(url_for('your_cookbook', username = session["username"]))

@app.route('/give_up/<recipe_id>')
def give_up(recipe_id):
    _recipe = mongo.db.recipes.update_one({"_id": ObjectId(recipe_id)},
        {'$inc': {"upvotes" : 1}})
    return redirect(url_for("show_recipe",recipe_id=recipe_id))

    
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
        dataset = dataset[:6]
        datanames = datanames[:6]
        
    return render_template("plot.html", 
    dataset = dataset,
    datanames = datanames,
    chart_type=chart_type)

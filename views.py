from flask import Flask, render_template, redirect, request, url_for, flash, session
import pymongo
from bson.objectid import ObjectId
from app import app
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
import os
from math import ceil
from flask import Blueprint
from basic import allowed_file, PER_PAGE, exclude_query, create_nice_date
from flask_paginate import Pagination, get_page_parameter


mongo = PyMongo(app)

def check_if_exists(field, value):
    if mongo.db.cookbooks.find_one({field: value}):
        return True
    else: 
        return False


def create_cookbook(cookbook_name='', password='', username='', description=''):
    """
    Inserts given parameters as a cookbook document to the db and returns it's id 
    """
    _id = ""
    if(check_if_exists("author_name", username) or check_if_exists("cookbook_name", cookbook_name)):
        return "Error! Username or cookbook's title already exists"
        
    else:
        _id=mongo.db.cookbooks.insert_one({"cookbook_name": cookbook_name,
            "password" : password,
            "author_name": username,
            "cookbook_desc": description,
            "created_on": create_nice_date(),
            "recipes_pinned": [],
            "recipes_owned": [],
            "recipes_number": 0
        })
        return _id

def update_recipes_array(recipe_id, recipe_title="", type_of_array='recipes_pinned', remove = False):
    """
    Function processing adding and removing recipe details from lists inside cookbook document. 
    Recipe_id, recipe_title - recipe's details
    type_of_array = default is pinned, but can get recipes_owned as well 
    remove - if true, it will remove recipe with details provided, if false, it will push it into list
    """
    if(remove == False):
        return mongo.db.cookbooks.update_one({'author_name': session.get('username')}, 
                { '$push': 
                    { type_of_array: 
                        {'_id': recipe_id, 'title': recipe_title}
                        
                    }}
                    )
    else:
        return  mongo.db.cookbooks.update_one({'author_name': session.get('username')}, 
                { '$pull': 
                    { type_of_array: 
                        {'_id': recipe_id}
                        
                    }}
                    )
                    
def remove_image(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    old_image =  recipe['image_url'].rsplit('/', 1)[1]
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], old_image))
    except Exception as e:
        print(e)
    
    
def find_recipe_id(field, value):
    _result = mongo.db.recipes.find_one({field: value})
    if _result:
        recipe_id = _result["_id"]
        return ObjectId(recipe_id)
    else: 
        return False


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
    This function takes optional arguments: 'dishes' or 'cuisines' to filter recipes by categories, and paginates
    them.
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
            record_name='recipes', link_size=8, css_framework='bootstrap4')
    # flash a message if there was no result
    if recipes.count()==0:
        flash("We couldn't get any records!")
    return render_template("recipes.html",
                pagination = pagination,
                recipes=recipes,
                cuisines=mongo.db.cuisines.find(),
                dishes=mongo.db.dishes.find())   
        

@app.route('/filter', methods=["GET", "POST"])
def filter_query():
    """
    Function is processing user's query.
    In POST request, it is processing form data into mongo db acceptable document, sends it to session to make
    pagination possible.
    In GET request, it gets ready query from session and sends to db. Then it either displays paginated results,
    or flashes a no result message.
    """
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
        
        # if there are some allergens to and keyword
        if (str_allergens!="" and query!=""):
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
        if(query_db):
            session['query_table'] = request.form
        recipes = mongo.db.recipes.find(query_db).skip(PER_PAGE * (page-1)).limit(PER_PAGE)
        if recipes.count()==0:
            flash("We found no results for your filters...try different ones")
        return redirect(url_for('filter_query'))
    else:
        result= session.get('query_table', {})
        query_db = session.get('query', {})
        recipes = mongo.db.recipes.find(query_db).skip(PER_PAGE * (page-1)).limit(PER_PAGE)
        if recipes.count()==0:
            flash("We found no results for your filters...try different ones")
        pagination = Pagination(page=page, total=recipes.count(), per_page=PER_PAGE,
                record_name='recipes',  bs_version=4)
        return render_template("recipes.html",
                            pagination = pagination,
                            recipes = recipes,
                            cuisines=mongo.db.cuisines.find(),
                            dishes=mongo.db.dishes.find(),
                            result = result
                            )

@app.route('/cancel_search')
def cancel_search():
    """
    Clears query value in session just in case of session expiring
    """
    try:
        session.pop('query')
    except(KeyError):
        redirect(url_for('get_recipes'))
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


@app.route('/cookbook_view/<ObjectId:cookbook_id>')
def cookbook_view(cookbook_id):
    """
    View is rendering cookbook details
    """
    _cookbook = mongo.db.cookbooks.find_one_or_404({"_id": cookbook_id})
    return render_template('cookbook_view.html',
    cookbook=_cookbook)
  
@app.route('/your_cookbook/<username>')
def your_cookbook(username=""):
    """
    Redirects to a cookbook view
    """
    if(username):
        _cookbook = mongo.db.cookbooks.find_one({"author_name": username})
    else:
        _cookbook = mongo.db.cookbooks.find_one({"author_name": session['username']})
    return redirect(url_for('cookbook_view', 
    cookbook_id = _cookbook["_id"]))

########################## Adding/showing/editing recipes logic ############################################################
    
@app.route('/show_recipe/<ObjectId:recipe_id>')
def show_recipe(recipe_id):
    """
    Shows recipe page, which contain recipe's details.
    """
    already_got = False
    owned = False
    _recipe = mongo.db.recipes.find_one_or_404({"_id": recipe_id})
    mongo.db.recipes.update_one({"_id": recipe_id},
        {'$inc': {"views" : 1}})
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

@app.route('/edit_recipe/<ObjectId:recipe_id>/<owned>')
def edit_recipe(recipe_id, owned):
    """
    Function that is getting recipe ready to edit. Finds recipe and passes it to template where it's 
    loaded into form, ready for the user to edit.
    """
    _recipe = mongo.db.recipes.find_one({"_id": recipe_id})
    
    ilist = _recipe['ingredients_list']
    plist = _recipe['preparation_steps_list']
    def gimme_ready_string(raw_list):
        """
        Gets list of strings, to concatenate it in one large string as it was before inserting into db
        """
        tmp = ""
        for item in raw_list:
            tmp += item + '\n'
        ready = tmp[:-2]
        return ready
    ing_string = gimme_ready_string(ilist)
    prep_string = gimme_ready_string(plist)
    return render_template('recipe_edit.html',
            recipe = _recipe,
            prep_string = prep_string,
            ing_string = ing_string,
            dishes=mongo.db.dishes.find(),
            cuisine_list=mongo.db.cuisines.find())

@app.route('/add_recipe')
def add_recipe():
    """
    Rendering form for adding a recipe. 
    """
    if('logged_in' in session and session['logged_in']==True):
        return render_template("add_recipe.html",
        dishes=mongo.db.dishes.find(),
        cuisine_list=mongo.db.cuisines.find())
    else:
        flash('You have to be logged in!')
        return redirect(url_for('get_recipes'))
    
    
@app.route('/update_recipe/<ObjectId:recipe_id>', methods=['POST'])
def update_recipe(recipe_id):
    """
    Updating recipe logic
    """
    request_ready = {}
    if( request.method == "POST"):
        # file processing, if any
        form = request.form.to_dict()
        username = form['author_name']
        """
        What's going on here: does the same as in insert recipe, however none of the fields in form is required, and "updated_on" field is created.
        """
        if request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                        result = mongo.db.cookbooks.find_one({"author_name": username})
                        number = int(result['recipes_number'])
                        filename = secure_filename(file.filename)
                        file_ext = filename[filename.rfind('.') : len(filename)+1].lower()
                        new_filename = username + str(number) + file_ext
                        file_path =  "uploaded_images/" + new_filename
                        # get me a full pathname and save the file
                        request_ready.setdefault("image_url", file_path)
                        remove_image(recipe_id)
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
                        mongo.db.cookbooks.update_one({"author_name": username}, {'$inc': {"recipes_number" : 1}})
            else:
                        flash("Incorrent file extension. Allowed extensions: png, jpg, jpeg or gif")
        
        for k, v in form.items():
                if ( k== "ingredients_list"):
                    request_ready.setdefault(k, v.splitlines())
                elif ( k== "preparation_steps_list"):
                    request_ready.setdefault(k, v.splitlines())
                else: 
                    request_ready[k] = v
        if(request_ready["cuisine_name"] == ""):
            del request_ready["cuisine_name"]
        new_date = create_nice_date()
        request_ready.setdefault("updated_on", new_date)
        result = mongo.db.recipes.update_one({"_id": recipe_id},
                                    {"$set": request_ready})
            
        if result.matched_count == 1:
            flash("Your changes have been saved")
        else:
            flash("There has been an error")
        return redirect(url_for('show_recipe', recipe_id=recipe_id))
    return redirect(url_for('show_recipe', recipe_id=recipe_id))
    
@app.route('/insert_recipe', methods=['POST'])
def insert_recipe():
    """
    Inserting recipe logic
    """
    recipes = mongo.db.recipes
    # creating an empty dictionary to send it later as a new document, to the database. 
    request_ready = {}
    if( request.method == "POST"):
        form = request.form
        username = request.form.to_dict()['author_name']
        # just validating recipe name, ingredients list, prep steps list and mostly important - if the name is unique. 
        # Others are not so important and they're validated with HTML5 anyway.
        if len(form["recipe_name"])>4 and len(form["ingredients_list"])>10 and len(form["preparation_steps_list"])>10 and find_recipe_id("recipe_name", form['recipe_name'])==False :

            new_date = create_nice_date()
            result = mongo.db.cookbooks.find_one({"author_name": username})
            number = int(result['recipes_number'])
            file = request.files['file']
            """
             filling disctionary with data from the form, with large strings sliced to an array
             and pushing and popping out some data
            """
            # empty image file will be prevented with js form validation
            if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # get me a full pathname and save the file
                    file_ext = filename[filename.rfind('.') : len(filename)+1].lower()
                    new_filename = username + str(number) + file_ext
                    file_path =  "uploaded_images/" + new_filename
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
            else:
                    flash("Incorrent file extension. Allowed extensions: png, jpg, jpeg or gif")
            for k, v in request.form.to_dict().items():
                if ( k== "ingredients_list"):
                    request_ready.setdefault(k, v.splitlines())
                elif ( k== "preparation_steps_list"):
                    request_ready.setdefault(k, v.splitlines())
                else: 
                    request_ready[k] = v
            if(request_ready["cuisine_name"] == ""):
                del request_ready["cuisine_name"] 
            # and adding some other initial data
            request_ready.setdefault("upvotes", 0)
            request_ready.setdefault("views", 0)
            request_ready.setdefault("created_on", new_date)
            request_ready.setdefault("image_url", file_path)
            #push everything to the database and store returned data in _result
            _result = recipes.insert_one(request_ready)
            if (username):
                # push to owned
                update_recipes_array(ObjectId(_result.inserted_id), request_ready['recipe_name'], type_of_array='recipes_owned')
                mongo.db.cookbooks.update_one({"author_name": username}, {'$inc': {"recipes_number" : 1}})
                flash("Your recipe has been saved!")
        else:
            flash("Some of your values were incorrent.")
    return redirect(url_for('get_recipes'))  
  
  
@app.route('/category_view/<collection_name>')
def category_view(collection_name):
    """
    View containing choice of collections either dishes or cuisines type
    """
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
    """
    Function passing user details to session. User is logged in.
    """
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
    # session.clear()
    session['logged_in'] = False
    session['username'] = ""
    return redirect(url_for('get_recipes'))    
    

############## Pinning/removing recipes logic############

@app.route('/pin_recipe/<ObjectId:recipe_id>/<recipe_title>')
def pin_recipe(recipe_id, recipe_title):
    """
    Recipe id and title is passed to update_recipe(), where it is added to 'pinned recipes' list in user's document in db
    """
    if(update_recipes_array(recipe_id, recipe_title = recipe_title)):
        mongo.db.recipes.update_one({"_id": recipe_id},
        {'$inc': {"upvotes" : 1}})
    return redirect(url_for('show_recipe', recipe_id=recipe_id))
   
@app.route('/remove_recipe/<ObjectId:recipe_id>/<owned>')
def remove_recipe(recipe_id, owned):
    """
    Function is passing correct arguments into update_recipes_array() function. It will remove from 'pinned recipes' list if it's just pinned,
    or remove completely form database and recipes_owned list if user is it's owner.
    """
    if(owned == "False"):
        if(update_recipes_array(recipe_id, remove = True)):
            mongo.db.recipes.update_one({"_id": ObjectId(recipe_id)},
            {'$inc': {"upvotes" : -1}})
            flash("Recipe has been unpinned!")
        return redirect(url_for('show_recipe', recipe_id=recipe_id))
    else:
        remove_image(recipe_id)
        mongo.db.recipes.delete_one({"_id": recipe_id})
        print('Removing!')
        update_recipes_array(recipe_id, type_of_array="recipes_owned", remove = True)
        flash("Recipe has been removed from database!")
        return redirect(url_for('get_recipes'))


    
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
        dataset = dataset[:8]
        datanames = datanames[:8]
        
    return render_template("plot.html", 
    dataset = dataset,
    datanames = datanames,
    chart_type=chart_type)

@app.route('/frequently_asked_questions')
def get_faq():
    """
    Displays FAQ
    """
    return render_template('faq.html')
    
################# last but not least ###############################
@app.errorhandler(404)
@app.errorhandler(400)
def page_not_found(e):
    """
    Error handling function
    """
    return render_template('error.html')
from app import app, mongo
import datetime
import os
import re
from flask import session
from bson.objectid import ObjectId


PER_PAGE = 12
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    """
    Checks if file has correct extension.
    COde copied form Flask documentation http://flask.pocoo.org/docs/0.12/patterns/fileuploads/
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

def exclude_query(request_ready):
    """
    Gets a dictionary as a parameter, converts into mongo search acceptable string
    ' -word1 -word2 -word3'. There is additional space at the begininig so it's ready
    to concatenate with query
    """
    str_allergens, allergens= "", ""
    for v in request_ready.values():
        if(v):
            temp = allergens
            proc = v.replace(" ", " -")
            allergens = temp + " -" + proc
    str_allergens = allergens[0:len(allergens)]
    return str_allergens


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
    

def create_nice_date():
    """
    Returns current date in dd-mm-yyyy format
    """
    now = datetime.datetime.now()
    new_date = "{0}-{1}-{2}".format(now.day,now.month,now.year)
    return new_date
 
 
def remove_image(recipe_id):
    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    old_image =  recipe['image_url'].rsplit('/', 1)[1]
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], old_image))
    
def find_recipe_id(field, value):
    _result = mongo.db.recipes.find_one({field: value})
    if _result:
        recipe_id = _result["_id"]
        return ObjectId(recipe_id)
    else: 
        return False
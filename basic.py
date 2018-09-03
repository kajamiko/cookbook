from app import app, mongo
import datetime
import os
import re
from flask import session


PER_PAGE = 6
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_if_exists(field, value):
    if mongo.db.cookbooks.find_one({field: value}):
        return True
    else: 
        return False

def get_record(collection, query={}):
    return collection.find_one(query)

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
            "recipes_owned": []
        })
        return _id

def exclude_query(request_ready):
    """
    passes strings into find query, converts to regexp
    """
    str_allergens, allergens = "", ""
    for k,v in request_ready.items():
        if(k):
            temp = str_allergens
            str_allergens = temp + v + " " 
            allergens = str_allergens.replace(' ', '|')
    str_allergens = allergens[0:len(allergens)-1]
    return str_allergens


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
 
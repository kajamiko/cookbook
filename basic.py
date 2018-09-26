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

    

def create_nice_date():
    """
    Returns current date in dd-mm-yyyy format
    """
    now = datetime.datetime.now()
    new_date = "{0}-{1}-{2}".format(now.day,now.month,now.year)
    return new_date
 
 

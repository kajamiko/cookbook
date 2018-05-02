import os
from flask import Flask, render_template, redirect, request, url_for
import pymongo
from flask_pymongo import PyMongo
from secret import db_name, uri_str 




app = Flask(__name__)
app.config["MONGO_DBNAME"] = db_name
app.config["MONGO_URI"] = uri_str

mongo = PyMongo(app)





if __name__ == "__main__":
    app.run(host=os.environ.get('IP'),
    port=int(os.environ.get('PORT')),
    debug=True)
import views
import run
import app
import os
import unittest

#c = run.app.test_client()

class TestCookbook(unittest.TestCase):
    
    def setUp(self):
        # run.app.config.from_object('conf.TestingConfig')
        # run.app.config["SERVER_NAME"] = "{0} {1}".format(os.environ.get('PORT'), os.environ.get('IP'))
        app = app.create_app()
        app.config["SERVER_NAME"] = "{0} {1}".format(os.environ.get('PORT'), os.environ.get('IP'))
        self.app = app.test_client() 
        
        
    def test_homepage(self):
        resp = self.app.get('/')
        self.assertEqual(resp._status_code, 200)
        
    def test_register(self):
        response = self.app.get('/add_recipe')
        self.assertEqual(response._status_code, 200)
    
    
    def test_dishes(self):
        response = self.app.get('/dishes/Italian')
        self.assertEqual(response._status_code, 200)
    
    def  test_creating_cookbook(self):
        
    # creates a document, gets its id and checks if it exists in database
        with run.app.app_context():
            
            username = "Lola"
            result=views.create_cookbook(cookbook_name="Lola_cookbook", password="", username=username)
            item=views.get_record(views.mongo.db.cookbooks, query={"author_name": username})
        self.assertEqual(result.inserted_id, item["_id"])
        
    def test_exist(self):
        with run.app.app_context():
            value = views.check_if_exists("author_name", "Lola")
          
        self.assertIsNone(value)
        
          
    # def  test_creating_cookbook(self):
        
    #     # creates a document, gets its id and checks if it exists in database
    #     with run.app.app_context():
            
    #         username = "Lola"
    #         result=views.create_cookbook(cookbook_name="Lola_cookbook", password="", username=username)
    #         item=views.get_record(views.mongo.db.cookbooks, query={"author_name": username})
        
    #     self.assertEqual(result.inserted_id, item["_id"])
        
        
    
    # def test_deleting(self):
    #     # queries for a document and delets it, then checks if succed
    #     with run.app.app_context():
    #         username = "Lola"
    #         item=views.get_record(views.mongo.db.cookbooks, query={"author_name": username})
            
    #     self.assertIsNotNone(item)
    #     with run.app.app_context():
    #         views.mongo.db.cookbooks.delete_one({"_id": item["_id"]})
    #         rmd =views.get_record(views.mongo.db.cookbooks, query={"author_name": username})
            
    #     self.assertIsNone(rmd)
        
            

if __name__ == '__main__':
    unittest.main()
import run
import unittest


#c = run.app.test_client()

class TestCookbook(unittest.TestCase):
    
        
    def test_exist(self):
        with run.app.app_context():
            value = run.check_if_exists("author_name", "Lola")
          
        self.assertIsNone(value)
          
    def  test_creating_cookbook(self):
        
        # creates a document, gets its id and checks if it exists in database
        with run.app.app_context():
            
            username = "Lola"
            result=run.create_cookbook(cookbook_name="Lola_cookbook", password="", username=username)
            item=run.get_record(run.mongo.db.cookbooks, query={"author_name": username})
        
        self.assertEqual(result.inserted_id, item["_id"])
        
        
    
    def test_deleting(self):
        # queries for a document and delets it, then checks if succed
        with run.app.app_context():
            username = "Lola"
            item=run.get_record(run.mongo.db.cookbooks, query={"author_name": username})
            
        self.assertIsNotNone(item)
        with run.app.app_context():
            run.mongo.db.cookbooks.delete_one({"_id": item["_id"]})
            rmd =run.get_record(run.mongo.db.cookbooks, query={"author_name": username})
            
        self.assertIsNone(rmd)
        
            

if __name__ == '__main__':
    unittest.main()
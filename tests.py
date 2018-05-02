import run
import unittest


#c = run.app.test_client()

class TestCookbook(unittest.TestCase):
    
    
    
    def test_home_page(self):
        
        self.assertEqual("hello", run.say_hello())
        
    def test_recipes(self):
        with run.app.app_context():
            self.assertIsNotNone(run.get_recipes(query={}))
          
          
    def  test_creating_cookbook(self):
        username = "Sebastian"
        with run.app.app_context():
            username = "Sebastian"
            created_id=run.create_cookbook(cookbook_name="Seb_cookbook", password="", username=username)
            item=run.get_cookbooks(query={"author_name": "Sebastian"})
    
            self.assertEquals(created_id, item.["_id"])
            

if __name__ == '__main__':
    unittest.main()
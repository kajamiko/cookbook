import views
import run
import app
import os
import unittest

#c = run.app.test_client()

class TestCookbook(unittest.TestCase):
    
    def setUp(self):
        app = app.create_app()
        app.config["SERVER_NAME"] = "{0} {1}".format(os.environ.get('PORT'), os.environ.get('IP'))
        self.app = app.test_client() 
        
        
    def test_homepage(self):
        resp = self.app.get('/')
        self.assertEqual(resp._status_code, 200)
        
    def test_rendering_add_page(self):
        response = self.app.get('/add_recipe')
        self.assertEqual(response._status_code, 200)

    
            

if __name__ == '__main__':
    unittest.main()

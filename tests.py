import views
from run import app
import os
from collections import OrderedDict
import basic
import unittest
from flask import session



class TestCookbook(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.application.config['SECRET_KEY'] = 'az#5t];a5g,dfnmk34;322bum'
        self.app.application.config['SESSION_COOKIE_DOMAIN'] = None
        self.app.application.config["SERVER_NAME"] = "{0} {1}".format(os.environ.get('PORT'), os.environ.get('IP'))
        # self.app.application.config['SERVER_NAME'] = 'localhost'
        
        
    def test_create_cookbook(self):
        """
        Checks different scenarios for creating cookbook function. Data is not validated
        """
        with app.app_context():
            result_id = basic.create_cookbook(cookbook_name='Lola', password='password', username='Lola', description='')
            self.assertIsNotNone(result_id)
            # testing that function rejects wrong values
            # self.assertEqual(basic.create_cookbook(cookbook_name='Lola', password='password', username='Lola', description=''), "Error! Username or cookbook's title already exists")
            self.assertEqual(basic.create_cookbook(cookbook_name='Lupa', password='password', username='Lola', description=''), "Error! Username or cookbook's title already exists")
            self.assertEqual(basic.create_cookbook(cookbook_name='Lola', password='password', username='Lupa', description=''), "Error! Username or cookbook's title already exists")
    
    def test_exclude_query(self):
        """
        See doc string for function. Checks if it's mongo search acceptable, however I'm passig sorted dict
        so the result can be asserted
        """
        my_dict = {"value": "some extra double ice-cream", "none": "", "cabbage": "cabbage"}
        
        self.assertEqual(basic.exclude_query(OrderedDict(sorted(my_dict.items(), key=lambda t: len(t[0])))),
                        ' -some -extra -double -ice-cream -cabbage')
                        
    def test_allowed_extensions(self):
        """
        Tests if the allowed_file funtion rejects unallowed extensions
        """
        self.assertFalse(basic.allowed_file('somefile.txt'))
        self.assertTrue(basic.allowed_file('somefile.png'))
            
    
    def test_homepage(self):
       with app.app_context():
            resp = self.app.get('/get_recipes')
            self.assertEqual(resp._status_code, 200)
            self.assertIn( 'Menu just for you', str(resp.data))

    def test_get_recipes(self):
       with app.app_context():
            resp = self.app.get('/')
            self.assertEqual(resp._status_code, 200)
            self.assertIn( 'Menu just for you', str(resp.data))

    def test_rendering_add_page(self):
        with app.app_context():
            response = self.app.get('/add_recipe')
            self.assertEqual(response._status_code, 200)
            
    def test_login(self):
        """
        Testing if loging in works properly
        """
        ### Unfortunetely does not give proper result due to issue with session testing
        with app.test_request_context('/login', method='POST', data=dict(author_name="Kajamiko",
                                        password="password")):
            resp = app.dispatch_request()
            self.assertIn('Logout', str(resp))
        # Checking if works and displays expected message
        with app.test_request_context('/login', method='POST', data=dict(author_name="Kittykat",
                                        password="password")):
            resp = app.dispatch_request()
            self.assertIn('user does not exist', str(resp))
        
        
    # def test_session(self):
    #     with app.test_client() as c:
    #         with app.test_request_context('/login', method='POST', data=dict(author_name="Kajamiko",
    #                                     password="password")):
    #             rv = app.dispatch_request()
    #             print(rv) dziala jesli złe dane podac
            
if __name__ == '__main__':
    unittest.main()

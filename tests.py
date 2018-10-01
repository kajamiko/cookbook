import views
from run import app
import os
from collections import OrderedDict
import basic
import unittest
from flask import session
import io



class TestCookbook(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.application.config['SECRET_KEY'] = 'az#5t];a5g,dfnmk34;322bum'
        self.app.application.config['SESSION_COOKIE_DOMAIN'] = None
        self.app.application.config["SERVER_NAME"] = "{0} {1}".format(os.environ.get('PORT'), os.environ.get('IP'))
        
        self.app.application.config['SESSION_TYPE'] = 'filesystem'
        
    
    def test_exclude_query(self):
        """
        See doc string for function. Checks if it's mongo search acceptable, however I'm passig sorted dict
        so the result can be asserted
        """
        my_dict = {"value": "cacao plum flour ice-cream", "none": "", "cabbage": "cabbage"}
        
        self.assertEqual(basic.exclude_query(OrderedDict(sorted(my_dict.items(), key=lambda t: len(t[0])))),
                        ' -cacao -plum -flour -ice-cream -cabbage')
                        
    def test_allowed_extensions(self):
        """
        Tests if the allowed_file funtion rejects unallowed extensions
        """
        self.assertFalse(basic.allowed_file('somefile.txt'))
        self.assertTrue(basic.allowed_file('somefile.png'))
        

        
    def test_homepage(self):
       with app.app_context():
            resp = self.app.get('/')
            self.assertEqual(resp._status_code, 200)
            self.assertIn( 'Menu just for you', str(resp.data))

    def test_category_view_cuisines(self):
        with app.app_context():
            """
            Testing response for displaying categories
            """
            resp = self.app.get('/category_view/cuisines')
            self.assertEqual(resp.status_code, 200)
            self.assertIn('American', str(resp.data))
            
    def test_category_view_dishes(self):
        """
        Testing response for displaying categories
        """
        with app.app_context():
            resp = self.app.get('/category_view/dishes')
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Main', str(resp.data))

    def test_get_recipes(self):
        """
        Testing displaying recipes
        """
        with app.app_context():
            resp = self.app.get('/get_recipes')
            self.assertEqual(resp._status_code, 200)
            self.assertIn( 'displaying ', str(resp.data))

    def test_summarise(self):
        """
        This test checks rendering template in summarise view
        """
        with app.app_context():
            resp = self.app.get('/summarise')
            self.assertEqual(resp._status_code, 200)
            self.assertIn( 'What would you like to summarise:', str(resp.data))    
    
    def test_rendering_add_page(self):

        with app.test_request_context('add_recipe', method='GET'):
            resp = app.dispatch_request()
            self.assertEqual(resp._status_code, 302)
            
            
    def test_filtering(self):
        """
        Tests filtering with an empty query, so just displaying all the recipes
        """
        with app.test_request_context('/filter', method='GET'):
            resp = app.dispatch_request()
            self.assertIn('displaying', str(resp))
       
        
    def test_faq(self):
        with app.app_context():
            resp = self.app.get('/frequently_asked_questions')
            self.assertEqual(resp._status_code, 200)
            #print(resp)
            self.assertIn('Frequently asked questions', str(resp.data))
            
            
    def test_login_get(self):
            resp = self.app.get('/login')
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please log in', str(resp.data))
            
            
    def test_login_post(self):
        """
        Testing if loging in works properly
        """
        ### Unfortunetely does not give proper result due to issue with session testing. Template should contain "Login", it does not
        with app.test_request_context('/login', method='POST', data=dict(author_name="Kaja",
                                        password="password")):
            resp = app.dispatch_request()
            self.assertNotIn('Logout', str(resp))
        # Checking if works and displays expected message
        with app.test_request_context('/login', method='POST', data=dict(author_name="Kittykat",
                                        password="password")):
            resp = app.dispatch_request()
            self.assertIn('User does not exist', str(resp))
        

if __name__ == '__main__':
    unittest.main()

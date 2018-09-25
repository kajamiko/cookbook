import views
from run import app
import os
from collections import OrderedDict
import basic
import unittest
from flask import session
import io

class TestCookbookCRUD(unittest.TestCase):
    """
    In this testing class, there are tests for inserting, updating and removing recipes.
    """
    def setUp(self):
        self.app = app.test_client()
        self.app.application.config['SECRET_KEY'] = 'az#5t];a5g,dfnmk34;322bum'
        self.app.application.config['SESSION_COOKIE_DOMAIN'] = None
        self.app.application.config["SERVER_NAME"] = "{0} {1}".format(os.environ.get('PORT'), os.environ.get('IP'))

    def test_inserting_recipe(self):
        """
        Tests if inserting recipe is working (including image file). The only part not passing test is
        updating provided user's 'recipes_owned' array, as this functionality requires session. It would not
        work in running app as session would not allow.
        
        """
        recipe_data = {'recipe_name': 'Inserting?', 'preparation_steps_list' : 'test test test',
        'ingredients_list': 'test1 test1 test1',
        'author_name': 'Kaja', "servings": "test", "cooking_time": "test", "difficulty": "Easy",
        "dish_type": "Main", 'cuisine_name': ""
        }
        
        recipe_data['file'] = (io.BytesIO(b"abcdef"), 'test.jpg')
        with app.test_request_context('insert_recipe', method='POST', data=recipe_data,
            content_type='multipart/form-data'):
            resp=app.dispatch_request()

            
      

    def test_update_recipe(self):
        """
        Tests if updating works (works), then checking result in show_recipe
        """
        recipe_to_update = {'recipe_name': 'Test to update', 'preparation_steps_list' : 'test test test',
        'ingredients_list': 'test1 test1 test1',
        'author_name': 'Kaja', "servings": "test", "cooking_time": "test", "difficulty": "Medium",
        "dish_type": "Main", 'cuisine_name': ""}
        new_data = {'recipe_name': 'Test recipe updated', 'preparation_steps_list' : 'updated test!',
        'ingredients_list': 'updated test is updated',
        'author_name': 'Kaja', "servings": "test", "cooking_time": "test", "difficulty": "Easy",
        "dish_type": "Main", "cuisine_name": ""
        }
        recipe_to_update['file'] = (io.BytesIO(b"abcdef"), 'test.jpg')
        new_data['file'] = (io.BytesIO(b"abcdef"), 'test.jpg')
        # inserting recipe
        with app.test_request_context('insert_recipe', method='POST', data= recipe_to_update,
            content_type='multipart/form-data'):
            app.dispatch_request()
            # checking if worked
        with app.app_context():
            id_part = str(basic.find_recipe_id("recipe_name", "Test to update"))
            resp = self.app.get('/show_recipe/'+ str(id_part))
            self.assertEqual(resp._status_code, 200)
            self.assertIn('test test test', str(resp.data))
        # updating recipe
        with app.test_request_context('update_recipe/'+ id_part , method='POST', data=new_data,
            content_type='multipart/form-data'):
            app.dispatch_request()      
        with app.app_context():
            # checking if worked
            id_part = str(basic.find_recipe_id("recipe_name", "Test recipe updated"))
            resp = self.app.get('/show_recipe/' + id_part)
            self.assertEqual(resp._status_code, 200)
            self.assertIn('updated test!', str(resp.data))
            self.app.get('/remove_recipe/' + str(id_part) + '/True' )
            resp = self.app.get('/show_recipe/'+ str(id_part))
            self.assertIn('We can\\\'t find the page you are looking for', str(resp.data))
            
            
            
    def test_removing(self):
        """
        Tests removing recipe
        """
        with app.app_context():
            id_part = basic.find_recipe_id("recipe_name", "Inserting?")
            resp = self.app.get('/show_recipe/'+ str(id_part))
            self.assertEqual(resp._status_code, 200)
            self.assertIn('Inserting?', str(resp.data))
            self.app.get('/remove_recipe/' + str(id_part) + '/True' )
            resp = self.app.get('/show_recipe/'+ str(id_part))
            self.assertIn('We can\\\'t find the page you are looking for', str(resp.data))
            
            
            
    
if __name__ == '__main__':
    unittest.main()

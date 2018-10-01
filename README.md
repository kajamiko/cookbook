# Yummy! Your online cookbook

Yummy! is an web application, allowing users to store and share their cooking recipes. It does not require any social networks account or email confirming. Just browse and add to your personal cookbook!


UX

My goal was to create a user-friendly web application, that will allow users to store cooking recipes and save them in one place without navigating between different pages, clearly separating user's own recipes from the ones made by others. I wanted to make it obvious, how to add a particular recipe into the cookbook. I wanted to make upvoting easy, so I linked it to pinning into cookbook.
My goal was also to make browsing other user's cookbook's possible, including the ones users are recommending, without linking it to any social networks.  In this meaning, it is completely safe - this website is all about cooking, not about who is cooking!

#### Users stories:

##### User type: 
As a cookbook user, I would like to store my recipes on my page, be able to easily browse them and edit if necessary.

As a page user, I would like to search through various recipes, excluding ones I know I won't like.

These files should themselves either be included in the project itself (in an separate directory), or just hosted elsewhere online and can be in any format that is viewable inside the browser.

## Features

1. Browsing feature
User can do following, without logging in:
- browse the recipes, either all of them or by categories
- filter search by keywords and/or categories

2. Cookbook feature
User is able to:
- create a cookbook
- login into it
- add new recipes, which will be displayed in 'own recipes' section
- pin other recipes to the cookbook, upvoting them in the same time


3. Statistic feature:
User can check following:
- see website's summary
- choose between categories or most active users
- change type of chart to display results. This function has no practical sense, but it looks nice.


## Existing Features

1. Browsing
- allows to browse all recipes, by clicking "Browse recipes" button on navigation bar or typing ".../get_recipes" in the browser bar
- user can browse by categories, by clicking "Dishes" or "Cuisines" buttons on navigation bar
- user can go to browsing page and filter search by filling form. There is keyword (search and/or exclude from search) functionality and categories functionality

2. Cookbook feature
- user may create his own cookbook, by filling and submitting the form on '.../register' page. User has to provide title for the cookbook, username he will be able to log in with, and password. Cookbook description is not mandatory.
- user can log in,  using his username and password.
- user can add new recipes by clicking green '+' button in his cookbook's "Recipes by <user>" section. This will redirect to '/add_recipe' page. All fields, except from "cuisine" field, are mandatory.
- user may edit his own recipes, by clicking yellow "Edit" button on recipe's page. This will redirect to '/edit_recipe' page, where a pre-filled form is rendered. All the values saved before will display in proper fields. All changes will be submitted by clicking "Save" button. 
- user can save other users' recipes by going to interesting recipe's page and clicking "Pin to your cookbook" button. The link to the recipe will appear in "Pinned recipes" section of user's cookbook.
- user may want to remove recipes form his cookbook, either directly form the cookbook view, by clicking a bin icon next to a recipe title, or from recipe page, by clicking "Remove" or "Unpin" button. If removing from cookbook page, a confirmation box will always pop out. However, when unpinning from recipe's page, there will be no confirmation box displayed, as it is obvious to pin it back, if done by mistake.
- it is possible to browse other users' cookbooks, however this function is available exclusively to logged in users.


3. Summary feature
- user can see website's summary, by clicking on 'Statistics' button on navigation bar. 
- user can choose between summarising categories or most active users, as well as choose a chart type, by submitting the form on the page.

## Future features
I do have many ideas of how to improve my application. Here are some of them:

1. First and most important is to make accounts secure and provide such features as retrieving forgotten passwords, disabling accounts.
3. Separating different parts of user's filter, so that user will be able to discard any filters without using query form again.
4. Re-structuring database by adding sub-categories.
5. Allowing users to search through all recipes stored in their cookbooks.
6. Probably less important, but so far editing recipe title is not validated. This bug has no effect on using deployed app, as the recipes are identified through their id field. However, it is a bit annoying in automated tests.

Technologies Used
In this section, you should mention all of the languages, frameworks, libraries, and any other tools that you have used to construct this project. For each, provide its name, a link to its official site and a short sentence of why it was used.

- HTML and CSS
    - project uses **HTML** and **CSS** to build webpages.
-  [Bootstrap](https://getbootstrap.com/)
    -project uses **Bootstrap** for webpages' layout.
- [Javascript](https://www.javascript.com/) 
    -The project uses **Javascript** to enhance pages functionality.
- [JQuery](https://jquery.com)
    - The project is using Bootstrap's **JQuery** for responsiveness.
- [Python](https://www.python.org/)
    - The project's back-end was written in **Python** .
- [Flask](http://flask.pocoo.org/)
    - project was built **flask** microframework due to its simplicity.
    - project uses **flask.session** for session functionality. 
- [MongoDB](https://www.mongodb.com/)
    - The project uses **MongoDB** database, mongod version 3.6.6..
- [Mlab](https://mlab.com/)
    - The project's database is hosted on **Mlab.com**.
- [Pymongo](https://pypi.org/project/pymongo/)
    - The project uses **Pymongo** as driver to connect to the database.
- [Flask-Pymongo](https://pypi.org/project/Flask-PyMongo/)
    - The project uses  **Flask-Pymongo** as a support for some tasks.
- [Flask-paginate](https://pythonhosted.org/Flask-paginate/)
    - The project uses **Flask-paginate** for pagination.

## Database 

As the project is using **mongodb**, I have just made a .docx file explaining documents' structure. It is stored in the project's /db folder.


For demostration purposes, the project's deployed version is configured to use populated database hosted on mlab.com. 
As images are stored in the project's filesystem, the deployed version is also populated with images.

## Testing

In this section, you need to convince the assessor that you have conducted enough testing to legitimately believe that the site works well. Essentially, in this part you will want to go over all of your user stories from the UX section and ensure that they all work as intended, with the project providing an easy and straightforward way for the users to achieve their goals.

All CRUD operations tests (for recipes) are in test_crud.py file. Known bugs for these operations:
- if a recipe is removed from the  owner's cookbook, other users' cookbooks are not updated. This means that it is possible to have "dead" links in "Pinned recipes" section. Clicking them will redirect to an error page. Links can always be deleted.
- when a recipe is about to be inserted, the name is checked for its uniqueness  before actual inserting. However, it is not the case when updating a recipe.It does not really affect the UX, because recipes documents are in fact identified with the "id" field.
- when inserting a recipe, it should normally be appended to "recipes_owned" array in cookbook's documents. Unfortunetely it is not working with automated tests because this operation is using flask.session. This functionality is well tested manually(see below).


All functions testing views are in test.py file.

### Unfortunetely, due to problems with testing flask.session, some of the automated tests are not working properly. However, these functionalities are properly tested manually.


For any scenarios that have not been automated, test the user stories manually and provide as much detail as is relevant. A particularly useful form for describing your testing process is via scenarios, such as:

Contact form:
Go to the "Contact Us" page
Try to submit the empty form and verify that an error message about the required fields appears
Try to submit the form with an invalid email address and verify that a relevant error message appears
Try to submit the form with all inputs valid and verify that a success message appears.
In addition, you should mention in this section how your project looks and works on different browsers and screen sizes.

You should also mention in this section any interesting bugs or problems you discovered during your testing, even if you haven't addressed them yet.


## Deployment

When deploying my application to Heroku, I have found that there is a cross import in my project. It used to work in development with no warnings. 
This is why I rearranged some parts of my code. Some of  the functions form 'basic.py' file to 'views.py' has been moved to make it work on Heroku. This does not actually affect the project's functionality, because not even a single line of code has been changed to achieve it. Therefore, I changed it only in 'master' branch. There is a separate 'test' branch, where things are left as they used to be before deployment.

For deployment, I had also changed some project's settings. Configuration variables were hard coded in a separate file out of the repository, so I changed it to use environmental variables, to make it work with Heroku.
Variables set in Heroku Config are: 'SECRET KEY', 'IP', 'PORT' and 'MONGO_URI'.


### How to run code locally for tests

##### Project's 'test' branch is configured specifically for tests. This includes:

- it's enough to set variables into file (see instruction below) to run the code. Master branch version is importing them form environment.
- exported database with minimum records to run project properly
- functions are printing success or fail messages into console. Master branch version doesn't have that functionality.

To run it:

1. Download repository's [test branch](https://github.com/kajamiko/cookbook/archive/test.zip).
2. Install dependencies listed in requirements.txt.
3. Import database from db/cookbook_proto to either local mongodb instance, or mlab online instance, using mogorestore. 
4. In app.py file, there is `from secret import secret_key, db_uri` line. These two values are then loaded as configuration values. 
    Create your won 'secret.py' file with values named above and the app is ready for testing.



## Credits

### Content

All the recipes and images picturing them have been copied from [Allrecipes](http://allrecipes.co.uk/).

### Media
The photos used in this site were obtained from [Allrecipes](http://allrecipes.co.uk/) and in some cases, from [Pixabay.com](https://pixabay.com/).

## Acknowledgements

Inspirations for this project was [Allrecipes](http://allrecipes.co.uk/)
- how they require users to upload for example, list of ingredients for a recipe. Of course I have no idea how it is implemented, but just watching gave me some hints.
- there is no requirements for image size, and also images displayed in search results are not statically sized, and I used a similar solution in my project.

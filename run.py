import os
import views







if __name__ == "__main__":
    views.app.jinja_env.auto_reload = True
    views.app.config['TEMPLATES_AUTO_RELOAD'] = True
    views.app.run(host=os.environ.get('IP'),
    port=int(os.environ.get('PORT')),
    debug=True)
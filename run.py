import os
import views
from app import app


if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host=os.environ.get('IP'),
    port=int(os.environ.get('PORT')),
    debug=False)
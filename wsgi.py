import os

from app import create_app
from config import config

# Create an application instance that web servers can use. We store it as
# "application" (the wsgi default) and also the much shorter and convenient
# "app".
application = app = create_app(os.environ.get('FLASK_CONFIG') or 'production')

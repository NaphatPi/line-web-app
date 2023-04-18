import os, dropbox
from flask import Flask
from datetime import timedelta
from flask_cors import CORS
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://') if os.environ.get('DATABASE_URL') is not None else 'sqlite:///database.db'
app.config['SSL_REDIRECT'] = True if os.environ.get('DYNO') else False

# LIFF 
app.config['LIFF_CHANNEL_ID'] = os.environ.get('LIFF_CHANNEL_ID')
app.config['LIFF_ID'] = os.environ.get('LIFF_ID')

# LINE BOT
app.config['CHANNEL_ACCESS_TOKEN'] = os.environ.get('CHANNEL_ACCESS_TOKEN')
app.config['CHANNEL_SECRET'] = os.environ.get('CHANNEL_SECRET')
app.config['MAIN_RICH_MENU'] = os.environ.get('MAIN_RICH_MENU')

app.permanent_session_lifetime = timedelta(minutes=30)
CORS(app)

login_manager = LoginManager(app)
login_manager.login_view = 'admin_login' #tell login manager what is the function name of our route; So login manager know where to redirect us when the pages require login
login_manager.login_message_category = 'info' #tell bootstrap the class of the message to display


db = SQLAlchemy(app)
from web_app.models import *
# db.create_all()
migrate = Migrate(app, db)

if app.config['SSL_REDIRECT']:
    from flask_sslify import SSLify
    sslify =  SSLify(app)
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)


app.config['DROP_BOX_TOKEN'] = os.environ.get('DROP_BOX_TOKEN')
app.config['DROP_BOX_PATH'] = '/docs' if os.environ.get('DYNO') else '/doc_temp'
dbx = dropbox.Dropbox(app.config['DROP_BOX_TOKEN'])


from web_app import routes

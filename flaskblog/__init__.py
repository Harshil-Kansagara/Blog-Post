from flask import Flask
import boto3
import botostubs
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

#db = boto3.resource('dynamodb', region_name='ap-south-1') # type: botostubs.DynamoDB
db = boto3.resource('dynamodb', endpoint_url='http://localhost:8000') # type: botostubs.DynamoDB
dbTableName = 'Blog'
table = db.Table(dbTableName)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY']='d425facdb1a4325328dc892f69cb5309'
    
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from flaskblog.users.routes import users
    from flaskblog.posts.routes import posts
    from flaskblog.main.routes import main
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)

    return app
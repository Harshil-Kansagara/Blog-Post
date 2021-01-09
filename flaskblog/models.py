import boto3
import botostubs
from flaskblog import db, dbTableName, login_manager, table
from flask_login import UserMixin
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError 

@login_manager.user_loader
def load_user(id):
    response = table.query(KeyConditionExpression=Key('Id').eq(id))
    if response['Items'] and  len(response['Items']) == 1:
        user = User(response['Items'][0]['Id'], response['Items'][0]['Username'], response['Items'][0]['Email'], response['Items'][0]['Password'])
        return user

class BlogDynamoDb():
    def create_blog_table(self):
        table = db.create_table(
            TableName=dbTableName,
            KeySchema=[
                {
                    'AttributeName':'Id',
                    'KeyType':'HASH' #partition key 
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'Id',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
        return table

class User(UserMixin):
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
    
    def __repr__(self):
        return f"User('{self.username}','{self.email}')"
    
    def get_id(self):
        return self.id

class Post():
    def __init__(self, id, user_id, title, content, date_posted, author):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.content = content
        self.date_posted = date_posted
        self.author = author

    def __repr__(self):
        return f"Post('{self.title}','{self.date_posted}', '{self.author}')"
    
    def get_id(self):
        return self.id
    

from flaskblog import dbTableName, table
from boto3.dynamodb.conditions import Attr
from flask import Flask, render_template, url_for, flash, redirect, request, abort, Blueprint
from flaskblog.models import Post
from flask_login import current_user

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def home():
    posts = []
    if current_user.is_authenticated:
        response = table.scan(FilterExpression=Attr('UserId').eq(current_user.id))
        if response['Items']:
            for i in response['Items']:
                post = Post(i['Id'], i['UserId'], i['Title'], i['Content'], i['Date_Posted'], current_user.username)
                posts.append(post)
    else:
        response = table.scan(
            FilterExpression=Attr('Username').not_exists()
        )
        if response['Items']:
            for i in response['Items']:
                user_response = table.scan(
                    FilterExpression=Attr('Id').eq(i['UserId'])
                )
                if user_response['Items'] and len(user_response['Items']).__eq__(1):
                    post = Post(i['Id'], i['UserId'], i['Title'], i['Content'], i['Date_Posted'], user_response['Items'][0]['Username'])
                    posts.append(post)
    return render_template('home.html', posts=posts, total_post = len(posts))

@main.route('/about')
def about():
    return render_template('about.html', title='About')

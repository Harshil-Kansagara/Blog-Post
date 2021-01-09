from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db, bcrypt, dbTableName, table
import uuid
from flaskblog.users.forms import RegistrationForm, LoginForm, UpdateAccountForm
from boto3.dynamodb.conditions import Attr
from flaskblog.models import User, Post

users = Blueprint('users',__name__)

@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        item = {
                'Id':str(uuid.uuid4()),
                'Username':form.username.data,
                'Email':form.email.data,
                'Password': hashed_password
            }
        table.put_item(Item=item)
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        response = table.scan(
            FilterExpression=Attr('Email').eq(form.email.data)
        )
        if response['Items'] and len(response['Items']) == 1:
            user = User(response['Items'][0]['Id'], response['Items'][0]['Username'], response['Items'][0]['Email'], response['Items'][0]['Password'])
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.home'))
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')
        else:
            flash('No user found with given email!', 'danger')
    return render_template('login.html', title='Login', form=form)

@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        response = table.update_item(
                Key={
                    'Id': current_user.id
                },
                UpdateExpression="set Username=:u, Email=:e",
                ExpressionAttributeValues={
                    ':u':form.username.data,
                    ':e':form.email.data
                },
                ReturnValues="UPDATED_NEW"
            )
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method.__eq__('GET'):
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account', form=form)

@users.route('/user/<string:user_id>')
def user_posts(user_id):
    posts=[]
    post_response = table.scan(
        FilterExpression=Attr('UserId').eq(user_id)
    )
    user_response = table.scan(FilterExpression=Attr('Id').eq(user_id))
    if user_response['Items'] and len(user_response['Items']).__eq__(1):
        user = User(user_response['Items'][0]['Id'], user_response['Items'][0]['Username'], user_response['Items'][0]['Email'], user_response['Items'][0]['Password'])
    if post_response['Items']:
        for i in post_response['Items']:
            post = Post(i['Id'], i['UserId'], i['Title'], i['Content'], i['Date_Posted'], user.username)
            posts.append(post)
    print(posts)
    return render_template('user_posts.html', posts=posts, user=user, total_post=len(posts))    

from flask import Flask, render_template, url_for, flash, redirect, request, abort, Blueprint
from flaskblog.posts.forms import PostForm
import uuid
from flask_login import current_user, login_required
from boto3.dynamodb.conditions import Attr
from datetime import datetime
from flaskblog import table
from flaskblog.models import Post

posts = Blueprint('posts', __name__)

@posts.route("/post/new", methods=['GET', 'POST'])
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        item = {
            'Id':str(uuid.uuid4()),
            'UserId': current_user.id,
            'Title':form.title.data,
            'Content':form.content.data,
            'Date_Posted':datetime.utcnow().strftime('%d-%m-%Y')
        }
        table.put_item(Item=item)
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')

@posts.route('/post/<string:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', title=post.title, post=post)

@posts.route('/post/<string:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = get_post(post_id)
    if post.user_id != current_user.id:
        abort(403)
    response = table.delete_item(
        Key={
            'Id':post_id
        }
    )
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))

@posts.route('/post/<string:post_id>/update', methods=['GET','POST'])
@login_required
def update_post(post_id):
    post = get_post(post_id)
    if post.user_id != current_user.id:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        response = table.update_item(
                Key={
                    'Id': post_id
                },
                UpdateExpression="set Title=:u, Content=:e",
                ExpressionAttributeValues={
                    ':u':form.title.data,
                    ':e':form.content.data
                },
                ReturnValues="UPDATED_NEW"
            )
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        print(post)
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')

def get_post(post_id):
    post_response= table.scan(
        FilterExpression=Attr('Id').eq(post_id)
    )
    if post_response['Items'] and len(post_response['Items']).__eq__(1):
        user_response = table.scan(
            FilterExpression=Attr('Id').eq(post_response['Items'][0]['UserId'])
        )
        if user_response['Items'] and len(user_response['Items']).__eq__(1):
            post = Post(post_response['Items'][0]['Id'], post_response['Items'][0]['UserId'], post_response['Items'][0]['Title'], post_response['Items'][0]['Content'], post_response['Items'][0]['Date_Posted'], user_response['Items'][0]['Username'])
            return post
    return Post()
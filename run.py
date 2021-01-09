from flaskblog import create_app
from flaskblog.models import BlogDynamoDb
from botocore.exceptions import ClientError

app = create_app()

if __name__ == "__main__":
    try:
        blogDynamoDb = BlogDynamoDb()
        table = blogDynamoDb.create_blog_table()
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            pass
    app.run(debug=True)


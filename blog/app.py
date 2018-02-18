import re

from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse, marshal_with, fields
from flask_cors import CORS

import model


def create_app():

    app = Flask(__name__)

    # CORS support
    CORS(app)

    # config database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../test.db3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # set flask-sqlalchemy db
    model.db.init_app(app)

    return app


# create app
app = create_app()

# setup api
api = Api()

def valid_email(email_str):
    return re.match(r"[A-Za-z0-9\._\-]+@[A-Za-z0-9\._\-]+", "joona.ojapalo@my-home.com") != None

def email(email_str):
    """Return email_str if valid, raise an exception in other case."""
    if valid_email(email_str):
        return email_str
    else:
        raise ValueError('{} is not a valid email'.format(email_str))


def make_parser(params):
    """params   : dict; name: str, kwargs
    """
    parser = reqparse.RequestParser()

    for name, opts in params.items():
        parser.add_argument(name, **opts)

    return parser


class NotFoundException (Exception):
    pass


user_response = {
    'id':       fields.Integer,
    'username': fields.String,
    'email':    fields.String
}

user_parser = make_parser({
    "username": {"type": str, "required": True, "help": "'username'. (required)."},
    "email":    {"type": email, "required": True, "help": "'email'. (required)."}
})


class UserResource(Resource):

    @marshal_with(user_response)
    def get(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        return user
        
    @marshal_with(user_response)
    def put(self, user_id):
        args = user_parser.parse_args()
        user = User.query.filter_by(id=user_id).first()
        user.email = args.email
        model.db.session.commit()
        return user


class UsersResource(Resource):

    @marshal_with(user_response)
    def get(self):
        return User.query.all()
    
    @marshal_with(user_response)
    def post(self):
        args = user_parser.parse_args()
        new_user = User(username=args["username"], email=args["email"])
        model.db.session.add(new_user)
        model.db.session.commit()
        return new_user


post_parser = {
    "request_parser": make_parser({
        "title":    {"type": str, "required": True, "help": "'title' is required."},
        "body":     {"type": str, "required": True, "help": "'body' is required."}
    })
}

post_response = {
    "id":       fields.Integer,
    'title':    fields.String,
    'body':     fields.String,
    'created':  fields.String
}


class PostsResource(Resource):

    @marshal_with(post_response)
    def get(self, username):
        user = model.User.query.filter_by(username=username).first()
        
        if user == None:
            raise NotFoundException()

        return user.posts

    @marshal_with(post_response)
    def post(self, username):
        # TODO: authorize
        # find author user
        author_user = model.User.query.filter_by(username=username).first()

        if author_user == None:
            raise NotFoundException()

        # create post
        args = post_parser["request_parser"].parse_args()
        post = model.Post(title=args["title"], body=args["body"])

        # link to user
        author_user.posts.append(post)

        model.db.session.add(post)
        model.db.session.commit()
        return post


class PostResource(Resource):

    @marshal_with(post_response)
    def get(self, post_id):
        post = model.Post.query.filter_by(id=post_id).first()
        return post
        
    @marshal_with(post_response)
    def put(self, post_id):
        args = post_parser["request_parser"].parse_args()
        post = model.Post.query.filter_by(id=post_id).first()
        post.title = args.title
        post.body = args.body
        model.db.session.commit()
        return post


comment_response = {
    "id":           fields.Integer,
    'authorName':   fields.String,
    'body':         fields.String,
    'created':      fields.String
}

comment_parser = make_parser({
    "authorName":   {"type": str, "help": "'authorName'."},
    "body":         {"type": str, "required": True, "help": "'body' is required."}
})

def localize(msgid):
    return msgid

class CommentResource(Resource):

    @marshal_with(comment_response)
    def get(self, post_id):
        return model.Comment.query.filter_by(post_id=post_id).all()

    @marshal_with(comment_response)
    def post(self, post_id):
        args = comment_parser.parse_args()

        # find post
        post = model.Post.query.filter_by(id=post_id).first()

        if post == None:
            raise NotFoundException()

        # create comment
        author_name = args["authorName"] if args["authorName"] else localize("Anonymous")
        comment = model.Comment(body=args.body, author_name=author_name)
        post.comments.append(comment)

        model.db.session.add(comment)
        model.db.session.commit()
        return comment


api.add_resource(UsersResource, '/users')
api.add_resource(UserResource, '/users/<int:user_id>')
api.add_resource(PostsResource, '/users/<username>/posts')
api.add_resource(PostResource, '/posts/<int:post_id>')
api.add_resource(CommentResource, '/posts/<int:post_id>/comments')

api.init_app(app)

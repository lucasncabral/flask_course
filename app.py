from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_restful import Api

from blocklist import BLOCKLIST
from resources.hotel import Hoteis, Hotel
from resources.site import Sites, Site
from resources.user import User, UserRegister, UserLogin, UserLogout, Users
from utils.http_status import *
from utils.messages import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['JWT_BLOCKLIST_ENABLE'] = True
api = Api(app)
jwt = JWTManager(app)


@app.before_first_request
def create_db():
    db.create_all()


@jwt.token_in_blocklist_loader
def check_blocklist(self, token):
    return token['jti'] in BLOCKLIST  # (unique identifier) of an encoded JWT


@jwt.revoked_token_loader
def invalid_access_token(jwt_header, jwt_payload):
    return jsonify({'message': YOU_HAVE_BEEN_LOGGED_OUT}), UNAUTHORIZED


# User Authentication
api.add_resource(UserRegister, '/register')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')

# User Profile
api.add_resource(Users, '/users')
api.add_resource(User, '/users/<string:login>')

# Post
# api.add_resource(PostRegister, '/post')

# Feed
# api.add_resource(feed, '/feed')

# Should be removed
api.add_resource(Hoteis, '/hoteis')
api.add_resource(Hotel, '/hoteis/<string:hotel_id>')
api.add_resource(Sites, '/sites')
api.add_resource(Site, '/sites/<string:url>')

if __name__ == '__main__':
    from sql_alchemy import db

    db.init_app(app)
    app.run(debug=True)

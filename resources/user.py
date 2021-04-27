from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp

from blocklist import BLOCKLIST
from models.user import UserModel
from utils.http_status import *
from utils.messages import *

attributes = reqparse.RequestParser()
attributes.add_argument('login', type=str, required=True, help=FIELD_CANNOT_BE_BLANK.format('login'))
attributes.add_argument('password', type=str, required=True, help=FIELD_CANNOT_BE_BLANK.format('password'))


class Users(Resource):
    # /users
    @jwt_required()
    def get(self):
        return {'users': [user.json() for user in UserModel.query.all()]}, OK


class User(Resource):
    # /{user_login}
    def get(self, login):
        user = UserModel.find_user(login)
        if user:
            return user.json(), OK
        return {'message':  NOT_FOUND.format('User', login)}, NOT_FOUND

    @jwt_required()
    def delete(self, login):
        user = UserModel.find_user(login)
        if user:
            try:
                user.delete_user()
            except Exception:
                return {'message': ERROR_WHEN_DELETING.format('user')}, SERVER_ERROR
            return {'message': ID_DELETED.format('User', login)}, OK
        return {'message': NOT_FOUND.format('User', login)}, NOT_FOUND


class UserRegister(Resource):
    # /register
    def post(self):
        data = attributes.parse_args()

        if UserModel.find_user(data['login']):
            return {'message': USER_ALREADY_REGISTERED.format(data['login'])}, NOT_FOUND

        user = UserModel(**data)
        user.save_user()
        return user.json(), 201


class UserLogin(Resource):
    # /login
    @classmethod
    def post(cls):
        dados = attributes.parse_args()

        user = UserModel.find_user(dados['login'])

        if user and safe_str_cmp(user.password, dados['password']):
            access_token = create_access_token(identity=user.user_id)
            return {'access_token': access_token}, OK
        return {'message': INCORRECT_USER_OR_PASSWORD}, UNAUTHORIZED


class UserLogout(Resource):
    # /logout
    @jwt_required()
    def post(self):
        jwt_id = get_jwt()['jti']
        BLOCKLIST.add(jwt_id)
        return {'message': LOGGED_OUT}, OK

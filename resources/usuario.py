from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import create_access_token, jwt_required, get_jwt

from blocklist import BLOCKLIST
from models.usuario import UserModel

atributos = reqparse.RequestParser()
atributos.add_argument('login', type=str, required=True, help='The field cannot be left blank')
atributos.add_argument('senha', type=str, required=True, help='The field cannot be left blank')


class User(Resource):
    # /usuarios/{user_id}
    def get(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            return user.json(), 200
        return {'message': 'User not found.'}, 404

    @jwt_required()
    def delete(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            try:
                user.delete_user()
            except Exception:
                return {'message': 'An internal error ocurred trying to delete user'}, 500
            return {"message": "User id '{}' deleted.".format(user_id)}, 200
        return {"message": "User id '{}' not found.".format(user_id)}, 404


class UserRegister(Resource):
    # /cadastro
    def post(self):
        dados = atributos.parse_args()

        if UserModel.find_by_login(dados['login']):
            return {"message": "The login '{}' already exists".format(dados['login'])}, 404

        user = UserModel(**dados)
        user.save_user()
        return user.json(), 201


class UserLogin(Resource):
    # /login
    @classmethod
    def post(cls):
        dados = atributos.parse_args()

        user = UserModel.find_by_login(dados['login'])

        if user and safe_str_cmp(user.senha, dados['senha']):
            token_de_acesso = create_access_token(identity=user.user_id)
            return {'access_token': token_de_acesso}, 200
        return {"message": "The username or password is incorrect"}, 401


class UserLogout(Resource):
    # /logout
    @jwt_required()
    def post(self):
        jwt_id = get_jwt()['jti']
        BLOCKLIST.add(jwt_id)
        return {"message": "Logged out successfully"}, 200

from flask_restful import Resource, reqparse
from models.hotel import HotelModel
from flask_jwt_extended import jwt_required
import sqlite3

from models.site import SiteModel
from resources.filtros import normalize_path_params, consulta_sem_cidade, consulta_com_cidade

path_params = reqparse.RequestParser()
path_params.add_argument('cidade', type=str)
path_params.add_argument('estrelas_min', type=float)
path_params.add_argument('estrelas_max', type=float)
path_params.add_argument('diaria_min', type=float)
path_params.add_argument('diaria_max', type=float)
path_params.add_argument('limit', type=float)
path_params.add_argument('offset', type=float)


class Hoteis(Resource):
    # /hoteis
    def get(self):
        connection = sqlite3.connect('banco.db')
        cursor = connection.cursor()
        dados = path_params.parse_args()
        dados_validos = {chave: dados[chave] for chave in dados if dados[chave] is not None}
        parameters = normalize_path_params(**dados_validos)

        consulta = consulta_sem_cidade if not parameters.get('cidade') else consulta_com_cidade
        tupla = tuple([parameters[chave] for chave in parameters])
        resultado = cursor.execute(consulta, tupla)

        hoteis = []
        for line in resultado:
            hoteis.append({
                'hotel_id': line[0], 'nome': line[1], 'estrelas': line[2], 'diaria': line[3], 'cidade': line[4],
                'site_id': line[5]
            })
        return {'hoteis': hoteis}


class Hotel(Resource):
    # /hotel/{id}
    argumentos = reqparse.RequestParser()
    argumentos.add_argument('nome', type=str, required=True, help='The field cannot be left blank')
    argumentos.add_argument('estrelas', type=float, required=True, help='The field cannot be left blank')
    argumentos.add_argument('diaria')
    argumentos.add_argument('cidade')
    argumentos.add_argument('site_id', type=int, required=True, help='Needs be linked with site')

    def get(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            return hotel.json(), 200
        return {'message': 'Hotel not found.'}, 404

    @jwt_required()
    def post(self, hotel_id):
        if HotelModel.find_hotel(hotel_id):
            return {"message": "Hotel id '{}' already exists.".format(hotel_id)}, 400
        dados = Hotel.argumentos.parse_args()
        hotel = HotelModel(hotel_id, **dados)

        if not SiteModel.find_by_id(dados.get('site_id')):
            return {'message': 'The hotel must be associated to a valid site id'}, 400

        try:
            hotel.save_hotel()
        except Exception:
            return {'message': 'An internal error ocurred trying to save hotel'}, 500
        return hotel.json(), 200

    @jwt_required()
    def put(self, hotel_id):
        dados = Hotel.argumentos.parse_args()
        hotel_encontrado = HotelModel.find_hotel(hotel_id)
        if hotel_encontrado:
            hotel_encontrado.update_hotel(**dados)
            hotel_encontrado.save_hotel()
            return hotel_encontrado.json(), 200
        hotel = HotelModel(hotel_id, **dados)
        try:
            hotel.save_hotel()
        except Exception:
            return {'message': 'An internal error ocurred trying to save hotel'}, 500
        return hotel.json(), 201

    @jwt_required()
    def delete(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            try:
                hotel.delete_hotel()
            except Exception:
                return {'message': 'An internal error ocurred trying to delete hotel'}, 500
            return {"message": "Hotel id '{}' deleted.".format(hotel_id)}, 200
        return {"message": "Hotel id '{}' not found.".format(hotel_id)}, 404

from flask import Flask, request, jsonify, make_response
import requests
import json
import random
from Autorizador import create_app
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity


app = create_app('default')
app_context = app.app_context()
app_context.push()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret'
api = Api(app)


ListaUsuarios = requests.get('http://127.0.0.1:5000/usuarios').json()
RegistroLogin = requests.get('http://127.0.0.1:5000/RegistroLogin').json()



class VistaAutorizador(Resource):

    def post(self): 
        ip_address = request.remote_addr     

        contrasena = request.json.get('contrasena')
        usuario = request.json.get('usuario')

        if any(i['usuario'] == usuario and i['contrasena'] == contrasena for i in ListaUsuarios):

            if usuario not in [entry['usuario'] for entry in RegistroLogin]:
                token = create_access_token(identity=usuario)
                return {'token': token}, 200
            else:
                user_entry = next(entry for entry in RegistroLogin if entry['usuario'] == usuario)

                if user_entry['ip_address'] == ip_address:
                    # Si la IP coincide, entregar el token
                    token = create_access_token(identity=usuario)
                    return {'token': token}, 200
                else:
                    return {'message': 'IP no autorizada'}, 401          

api.add_resource(VistaAutorizador, '/autorizador')
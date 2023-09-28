from flask import Flask, request
import requests
import json
import random
from Autorizador import create_app
from flask_restful import Api, Resource
from flask_jwt_extended import create_access_token,JWTManager,jwt_required
from datetime import datetime


app = create_app('default')
app_context = app.app_context()
app_context.push()

jwt = JWTManager(app)
api = Api(app)

ListaUsuarios = requests.get('http://127.0.0.1:5000/usuarios').json()
RegistroLogin = requests.get('http://127.0.0.1:5000/RegistroLogin').json()

fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class VistaAutorizador(Resource):

    def post(self): 
        ip_address = request.remote_addr     

        contrasena = request.json.get('contrasena')
        usuario = request.json.get('usuario')

        registro_Login = {
        'usuario': usuario,
        'ip_address': ip_address,
        'fecha_hora': fecha_hora_actual
}
        if any(i['usuario'] == usuario and i['contrasena'] == contrasena for i in ListaUsuarios):

            if usuario not in [entry['usuario'] for entry in RegistroLogin]:
                token = create_access_token(identity=usuario)
                requests.post('http://127.0.0.1:5000/ResigroLogin', json=registro_Login)
                return {'token': token}, 200
            else:
                user_entry = next(entry for entry in RegistroLogin if entry['usuario'] == usuario)

                if user_entry['ip_address'] == ip_address:
                    # Si la IP coincide, entregar el token
                    token = create_access_token(identity=usuario)
                    requests.post('http://127.0.0.1:5000/ResigroLogin', json=registro_Login)
                    return {'token': token}, 200
                else:
                    return {'message': 'IP no autorizada'}, 401          

api.add_resource(VistaAutorizador, '/autorizador')
from flask import Flask, request
import requests
import platform
import socket
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

fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class VistaAutorizador(Resource):

    @staticmethod
    def obtener_info_geografica(ip):
        url = f"https://ipinfo.io/{ip}/json"
        response = requests.get(url)
        data = response.json()
        return data
    
    @staticmethod
    def obtener_info_sistema():
        sistema_operativo = platform.system()
        nombre_equipo = socket.gethostname()
        return {'sistema_operativo': sistema_operativo, 'nombre_equipo': nombre_equipo}

    def post(self):
        contrasena = request.json.get('contrasena')
        usuario =  {'usuario':request.json.get('usuario')} 

        response = requests.get('http://127.0.0.1:5000/usuario', json=usuario)

        if response.status_code == 200:
            InfoUsuario = response.json()
            RegistroLogin = InfoUsuario['loginHistorical']

            ip_address = request.remote_addr
            info_geografica = requests.obtener_info_geografica(ip_address)        
            info_sistema = requests.obtener_info_sistema()
            

            registro_Login = {
                'idUsuario':InfoUsuario['id'],
                'fecha': fecha_hora_actual,
                'ip': ip_address,            
                'paisIp': info_geografica.get('country'),
                'ciudadIp': info_geografica.get('city'),
                'sistemaOperativo': info_sistema.get('sistema_operativo'),
                'nombreEquipo': info_sistema.get('nombre_equipo')
                }
            
            if contrasena == InfoUsuario['contrasena']:

                # Si el usuario no tiene registros de login, entregar el token
                if usuario not in [entry['usuario'] for entry in RegistroLogin]:
                    token = create_access_token(identity=usuario)
                    requests.post('http://127.0.0.1:5000/ResigroLogin', json=registro_Login)
                    return {'token': token}, 200
                
                # Si el usuario tiene registros de login, validar si el registro actual es igual a alguno de los registros anteriores
                else:
                    registroEncontrado=False

                    for registro in RegistroLogin:

                        if (
                            registro['ip'] == ip_address and
                            registro['paisIp'] == registro_Login['paisIp'] and
                            registro['ciudadIp'] == registro_Login['ciudadIp'] and
                            registro['sistemaOperativo'] == registro_Login['sistemaOperativo'] and
                            registro['nombreEquipo'] == registro_Login['nombreEquipo']
                        ):
                            registroEncontrado = True
                            break
                        else:
                            return {'message': 'Se requiere doble Autenticacion'}, 401
                
                    if registroEncontrado == False:
                        return {'message': 'Se requiere doble Autenticacion'}, 401
                    else:
                            token = create_access_token(identity=usuario)
                            requests.post('http://127.0.0.1:5000/ResigroLogin', json=registro_Login)
                            return {'token': token}, 200   


            else:
                return {'message': 'Credenciales incorrectas'}, 401
        else:
            return {'message': 'Usuario no existe'}, 401          

api.add_resource(VistaAutorizador, '/autorizador')
from flask import Flask, request
from faker import Faker
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

fake = Faker()

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

    def get(self):
        ataqueIntroducido = request.json.get('ataqueIntroducido')
        contrasena = request.json.get('contrasena')
        usuario =  {'usuario':request.json.get('usuario')} 


        response = requests.get('http://127.0.0.1:5000/usuario', json=usuario)

        if response.status_code == 200:
            InfoUsuario = response.json()
            RegistroLogin = InfoUsuario['loginHistorical']

            if InfoUsuario['canalDobleAutenticacion'] == 'TELEFONO':
                accion = 'ENVIO_MENSAJE_TEXTO'
            else:
                accion = 'ENVIO_MENSAJE_CORREO'

            

            if  ataqueIntroducido == True:
                ip_address = fake.ipv4()
            else:   
                ip_address = request.remote_addr

            
            info_geografica = requests.obtener_info_geografica(ip_address)        
            info_sistema = requests.obtener_info_sistema()
            
          
            if contrasena == InfoUsuario['contrasena']:

                # Si el usuario no tiene registros de login, entregar el token
                if len(RegistroLogin)==0:
                    token = create_access_token(identity=usuario)
                    registro_Login = {
                        'idUsuario':InfoUsuario['id'],
                        'fecha': fecha_hora_actual,
                        'ip': ip_address,            
                        'paisIp': info_geografica.get('country'),
                        'ciudadIp': info_geografica.get('city'),
                        'sistemaOperativo': info_sistema.get('sistema_operativo'),
                        'nombreEquipo': info_sistema.get('nombre_equipo'),
                        'tipoActividad': 'CONFIABLE',
                        'accion': 'NINGUNA',
                        'ataqueIntroducido': ataqueIntroducido
                    }
                    requests.post('http://127.0.0.1:5000/loginhistory', json=registro_Login)
                    return {'token': token}, 200
                
                # Si el usuario tiene registros de login, validar si el registro actual es igual a alguno de los registros anteriores
                else:
                    registroEncontrado=False

                    for registro in RegistroLogin:

                        if (
                            registro['ip'] == ip_address and
                            registro['paisIp'] == info_geografica.get('country') and
                            registro['ciudadIp'] == info_geografica.get('city') and
                            registro['sistemaOperativo'] == info_sistema.get('sistema_operativo') and
                            registro['nombreEquipo'] == info_sistema.get('nombre_equipo')
                        ):
                            registroEncontrado = True
                            break

                
                    if registroEncontrado == False:
                        registro_Login = {
                            'idUsuario':InfoUsuario['id'],
                            'fecha': fecha_hora_actual,
                            'ip': ip_address,            
                            'paisIp': info_geografica.get('country'),
                            'ciudadIp': info_geografica.get('city'),
                            'sistemaOperativo': info_sistema.get('sistema_operativo'),
                            'nombreEquipo': info_sistema.get('nombre_equipo'),
                            'tipoActividad': 'SOSPECHOSA',
                            'accion': accion,
                            'ataqueIntroducido': ataqueIntroducido
                        }
                        requests.post('http://127.0.0.1:5000/loginhistory', json=registro_Login)
                        return {'message': 'Se requiere doble Autenticacion'}, 401
                    else:
                            registro_Login = {
                                'idUsuario':InfoUsuario['id'],
                                'fecha': fecha_hora_actual,
                                'ip': ip_address,            
                                'paisIp': info_geografica.get('country'),
                                'ciudadIp': info_geografica.get('city'),
                                'sistemaOperativo': info_sistema.get('sistema_operativo'),
                                'nombreEquipo': info_sistema.get('nombre_equipo'),
                                'tipoActividad': 'CONFIABLE',
                                'accion': 'NINGUNA',
                                'ataqueIntroducido': ataqueIntroducido
                            }

                            token = create_access_token(identity=usuario)
                            requests.post('http://127.0.0.1:5000/loginhistory', json=registro_Login)
                            return {'token': token}, 200   


            else:
                registro_Login = {
                    'idUsuario':InfoUsuario['id'],
                    'fecha': fecha_hora_actual,
                    'ip': ip_address,            
                    'paisIp': info_geografica.get('country'),
                    'ciudadIp': info_geografica.get('city'),
                    'sistemaOperativo': info_sistema.get('sistema_operativo'),
                    'nombreEquipo': info_sistema.get('nombre_equipo'),
                    'tipoActividad': 'CREDENCIALES_INCORRECTAS',
                    'accion': 'NINGUNA',
                    'ataqueIntroducido': ataqueIntroducido
                }
                requests.post('http://127.0.0.1:5000/loginhistory', json=registro_Login)

                return {'message': 'Credenciales incorrectas'}, 401
        else:
            return {'message': 'Usuario no existe'}, 401          

api.add_resource(VistaAutorizador, '/autorizador')
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', ssl_context='adhoc', port=6000)
from celery import Celery
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

#Integracion con la cola de mensajes
celery_app= Celery(__name__, broker='redis://localhost:6379/0')
@celery_app.task(name='doble_autenticacion')
def notificar_csv(*args):
    pass

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
    
    @staticmethod
    def dobleAutenticacion(data):
            #Envio de mensaje a la cola del log en formato json
            log = {
                "usuario" : data['usuario'],
                "canal" : data['canalDobleAutenticacion']['llave'],
                "telefono" : data["telefono"],
                "correo" : data['correoElectronico']
            }
            #convertir log en una tupla para que vaya a la cola
            args=(
                log["usuario"],
                log["canal"],
                log["telefono"],
                log["correo"]
            )
            #enviar a la cola    
            notificar_csv.apply_async(args, queue='colaValidacion')


    def get(self):
        ataqueIntroducido = request.json.get('ataqueIntroducido')
        contrasena = request.json.get('contrasena')
        usuario =  {'usuario':request.json.get('usuario')} 

        

        response = requests.get('https://127.0.0.1:5000/usuario', json=usuario,verify=False)
        

        if response.status_code == 200:
            InfoUsuario = response.json()
            RegistroLogin = InfoUsuario['loginHistorical']

            if InfoUsuario['canalDobleAutenticacion']['llave'] == 'TELEFONO':
                accion = 'ENVIO_MENSAJE_TEXTO'
            else:
                accion = 'ENVIO_MENSAJE_CORREO'

            

            if  ataqueIntroducido == True:
                ip_address = fake.ipv4()
                sistema_operativo = fake.random_element(elements=("Windows 10", "macOS", "Linux"))
                nombre_equipo = fake.company()
                info_sistema = {'sistema_operativo': sistema_operativo, 'nombre_equipo': nombre_equipo}
                
            else:   
                ip_address = request.remote_addr
                if ip_address == "127.0.0.1":
                    ip_address="187.134.191.64"
                        
                info_sistema = VistaAutorizador.obtener_info_sistema()

            info_geografica = VistaAutorizador.obtener_info_geografica(ip_address)
            
            
            
          
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
                    requests.post('https://127.0.0.1:5000/loginhistory', json=registro_Login,verify=False)
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
                        requests.post('https://127.0.0.1:5000/loginhistory', json=registro_Login,verify=False)

                        VistaAutorizador.dobleAutenticacion(InfoUsuario)
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
                            requests.post('https://127.0.0.1:5000/loginhistory', json=registro_Login,verify=False)
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
                requests.post('https://127.0.0.1:5000/loginhistory', json=registro_Login,verify=False)

                return {'message': 'Credenciales incorrectas'}, 401
        else:
            return {'message': 'Usuario no existe'}, 401          

api.add_resource(VistaAutorizador, '/autorizador')
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', ssl_context='adhoc', port=6000)
import datetime
from pydoc import describe
from flask import request
from .modelos import db, LoginHistorical,LoginHistoricalSchema, Usuario, UsuarioSchema,  LoginHistorical
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

usuario_schema = UsuarioSchema()
login_schema = LoginHistoricalSchema()


class VistaUsuario(Resource):
    def post(self):
        # Obtener los datos JSON de la solicitud
        data = request.json

        # Crear un nuevo usuario
        nuevo_usuario = Usuario(
            usuario=data['usuario'],
            contrasena=data['contrasena'],
            correoElectronico=data['correoElectronico'],
            telefono=data['telefono'],
            canalDobleAutenticacion=data['canalDobleAutenticacion'],
        )

        # Agregar y guardar el nuevo usuario en la base de datos
        db.session.add(nuevo_usuario)
        db.session.commit()
        return usuario_schema.dump(nuevo_usuario), 201
    
    def get(self):
        usuario_string = request.json.get('usuario')
        # Consulta los usuarios y ordénalos por nombre en orden descendente 
        usuario = Usuario.query.filter_by(usuario=usuario_string).first()

        # Serializa y devuelve los resultados (regresar un solo usuario.usuario .first)
        return usuario_schema.dump(usuario)
    

class VistaLoginHistorical(Resource):
    def post(self):
        # Obtener los datos JSON de la solicitud
        data = request.get_json()
        data["fecha"] = datetime.datetime.fromisoformat(data["fecha"])
        
        # Crear un registro de Login
        nuevo_login = LoginHistorical(
            idUsuario=data['idUsuario'],
            fecha=data['fecha'],
            ip=data['ip'],
            paisIp=data['paisIp'],
            ciudadIp=data['ciudadIp'],
            sistemaOperativo=data['sistemaOperativo'],
            nombreEquipo=data['nombreEquipo'],
            tipoActividad=data['tipoActividad'],
            accion=data['accion'],
            ataqueIntroducido=data['ataqueIntroducido']
        )

        # Agregar y guardar el nuevo usuario en la base de datos
        db.session.add(nuevo_login)
        db.session.commit()
        return login_schema.dump(nuevo_login), 201
    




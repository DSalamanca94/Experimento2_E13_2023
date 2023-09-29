from pydoc import describe
from flask import request
from .modelos import db, LoginHistorical,  Usuario, UsuarioSchema,  LoginHistorical, TipoActividad, TiposActividad, AccionDobleAutenticacion, AccionesDobleAutenticacionSchema, CanalDobleAutenticacion, CanalesDobleAutenticacionSchema, TiposActividadSchema   
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

usuario_schema = UsuarioSchema()


class VistaUsuario(Resource):
    def post(self):
        # Obtener los datos JSON de la solicitud
        data = request.json

        # Crear un nuevo usuario
        nuevo_usuario = Usuario(
            idUsuario = data['id'],
            Usuario=data['usuario'],
            contrasenaUsuario=data['contrasena'],
            correoElectronicoUsuario=data['correoElectronico'],
            telefonoUsuario=data['telefono'],
            canalDobleAutenticacion=data['canalDobleAutenticacion'],
        )


        # Crear canales de doble autenticación asociadas al  usuario
        for canales_data in data['canalDobleAutenticacion']:
            nuevo_canal = CanalesDobleAutenticacionSchema(
                nombreCanalDobleAutenticacion=canales_data['nombreCanalDobleAutenticacion']
            )
            nuevo_usuario.canalDobleAutenticacion.append(nuevo_canal)

        # Agregar y guardar el nuevo usuario en la base de datos
        db.session.add(nuevo_usuario)
        db.session.commit()
        return usuario_schema.dump(nuevo_usuario), 201
    

class VistaLoginHistorical(Resource):
    def post(self):
        # Obtener los datos JSON de la solicitud
        data = request.json

        # Crear un registro de Login
        nuevo_login = LoginHistorical(
            id=data['id'],
            idUsuario=data['idUsuario'],
            fechaLogin=data['fecha'],
            ipLogin=data['ip'],
            passaisIpLogin=data['paisIp'],
            ciudadIpLogin=data['ciudadIP'],
            sistemaOperativoLogin=data['sistemaOperativo'],
            nombreEquipoLogin=data['nombreEquipo '],
            tipoActividadLogin=data['tipoActividad'],
            accionLogin=data['accion'],
            ataqueIntroducidoLogin=data['ataqueIntroducido']
        )


        # Crear tipos de actividades asociadas al Login
        for tipos_data in data['tipoActividadLogin']:
            nuevo_tipo_Actividad = TiposActividadSchema(
                nombreCanalDobleAutenticacion=tipos_data['nombreCanalDobleAutenticacion']
            )
            nuevo_login.tipoActividad.append(nuevo_tipo_Actividad)



        # Crear acciones asociadas al Login
        for acciones_data in data['accionLogin']:
            nueva_accion = AccionesDobleAutenticacionSchema(
                nombreAccionesDobleAutenticacion=acciones_data['nombreAccionesDobleAutenticacion']
            )
            nuevo_login.accion.append(nueva_accion)


        # Agregar y guardar el nuevo usuario en la base de datos
        db.session.add(nuevo_login)
        db.session.commit()
        return usuario_schema.dump(nuevo_login), 201
    

       
    def get(self):
        # Consulta los usuarios y ordénalos por nombre en orden descendente 
        usuarios = Usuario.query.order_by(Usuario.usuario.asc()).all()    

        # Serializa y devuelve los resultados (regresar un solo usuario.usuario .first)
        return Usuario.first




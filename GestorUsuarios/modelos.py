from flask_sqlalchemy import SQLAlchemy
import enum

db = SQLAlchemy()

class TipoActividad(enum.Enum):
   CONFIABLE = 1
   SOSPECHOSA = 2

class AccionDobleAutenticacion(enum.Enum):
   NINGUNA = 1
   ENVIO_MENSAJE_TEXTO = 2
   ENVIO_MENSAJE_CORREO = 3   

class CanalDobleAutenticacion(enum.Enum):
   TELEFONO = 1
   CORREO_ELECTRONICO = 2

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    usuario = db.Column(db.String(128))
    contrasena = db.Column(db.String(128))
    correoElectronico = db.Column(db.String(128))
    telefono = db.Column(db.String(128))
    canalDobleAutenticacion = db.Column(db.Enum(CanalDobleAutenticacion))

class LoginHistorical (db.Model):
    id = db.Column(db.Integer, primary_key = True)
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    fecha = db.Column(db.DateTime)
    #datosGeolocalizacion 
    ip = db.Column(db.String(128))
    paisIp = db.Column(db.String(128))
    cuidadIp   = db.Column(db.String(128))
    sistemaOperativo = db.Column(db.String(128))
    nombreEquipo = db.Column(db.String(128))
    #datosAnalisis
    tipoActividad = db.Column(db.Enum(TipoActividad))
    accion= db.Column(db.Enum(AccionDobleAutenticacion))
    ataqueIntroducido= db.Column(db.Boolean) #True si el ataque fue introducido por el usuario, False si es una actividad normal
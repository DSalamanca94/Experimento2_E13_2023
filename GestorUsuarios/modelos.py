from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
import enum

db = SQLAlchemy()

class TipoActividad(enum.Enum):
   CONFIABLE = 1
   SOSPECHOSA = 2
   CREDENCIALES_INCORRECTAS = 3

class AccionDobleAutenticacion(enum.Enum):
   NINGUNA = 1
   ENVIO_MENSAJE_TEXTO = 2
   ENVIO_MENSAJE_CORREO = 3   

class CanalDobleAutenticacion(enum.Enum):
   TELEFONO = 1
   CORREO_ELECTRONICO = 2


class EnumADiccionario(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return {"llave": value.name, "valor": value.value}


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    usuario = db.Column(db.String(128))
    contrasena = db.Column(db.String(128))
    correoElectronico = db.Column(db.String(128))
    telefono = db.Column(db.String(128))
    canalDobleAutenticacion = db.Column(db.Enum(CanalDobleAutenticacion))
    loginHistorical = db.relationship('LoginHistorical', backref='usuario', lazy=True, cascade='all, delete-orphan')

class LoginHistorical (db.Model):
    id = db.Column(db.Integer, primary_key = True)
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    fecha = db.Column(db.DateTime)
    #datosGeolocalizacion 
    ip = db.Column(db.String(128))
    paisIp = db.Column(db.String(128))
    ciudadIp   = db.Column(db.String(128))
    sistemaOperativo = db.Column(db.String(128))
    nombreEquipo = db.Column(db.String(128))
    #datosAnalisis
    tipoActividad = db.Column(db.Enum(TipoActividad))
    accion= db.Column(db.Enum(AccionDobleAutenticacion))
    ataqueIntroducido= db.Column(db.Boolean) #True si el ataque fue introducido por el usuario, False si es una actividad normal

class UsuarioSchema(SQLAlchemyAutoSchema):
    canalDobleAutenticacionUsuario= EnumADiccionario(attribute=("canalDobleAutenticacionUsuario"))
    loginHistorical = fields.Nested('LoginHistoricalSchema', many=True)

    class Meta:
         model = Usuario
         include_relationships = True
         load_instance = True 

class LoginHistoricalSchema(SQLAlchemyAutoSchema):
    tipoActividad = EnumADiccionario(attribute=("tipoActividad"))
    accion = EnumADiccionario(attribute=("accion"))
    
    class Meta:
         model = LoginHistorical
         include_relationships = True
         load_instance = True   


            
class TiposActividad(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nombreTipoActividad = db.Column(db.Enum(TipoActividad))
    Usuario=db.Column(db.Integer, db.ForeignKey('usuario.id'))

class TiposActividadSchema(SQLAlchemyAutoSchema):
    nombreTipoActividad = EnumADiccionario(attribute=("nombreTipoaActividad"))
    class Meta:
        model = TiposActividad
        include_relationships = True
        load_instance = True      



class AccionesDobleAutenticacion(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nombreAccionDobleAutenticacion = db.Column(db.Enum(AccionDobleAutenticacion))
    Usuario=db.Column(db.Integer, db.ForeignKey('usuario.id'))

class AccionesDobleAutenticacionSchema(SQLAlchemyAutoSchema):
    nombreAccionDobleAutenticacion = EnumADiccionario(attribute=("nombreAccionDobleAutenticacion"))
    class Meta:
        model = AccionesDobleAutenticacion
        include_relationships = True
        load_instance = True      



class CanalesDobleAutenticacion(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nombreCanalDobleAutenticacion = db.Column(db.Enum(CanalDobleAutenticacion))
    Usuario=db.Column(db.Integer, db.ForeignKey('usuario.id'))

class CanalesDobleAutenticacionSchema(SQLAlchemyAutoSchema):
    nombreCanalDobleAutenticacion = EnumADiccionario(attribute=("nombreAccionDobleAutenticacion"))
    class Meta:
        model = CanalesDobleAutenticacion
        include_relationships = True
        load_instance = True      


from flask_sqlalchemy import SQLAlchemy
import enum

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    usuario = db.Column(db.String(128))
    contrasena = db.Column(db.String(128))

class LoginHistorical (db.Model):
    id = db.Column(db.Integer, primary_key = True)
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    fecha = db.Column(db.DateTime)
    ip = db.Column(db.String(128))
    paisIp = db.Column(db.String(128))
    cuidadaIP   = db.Column(db.String(128))
    sistemaOperativo = db.Column(db.String(128))
    nombreEquipo = db.Column(db.String(128))
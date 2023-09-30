from GestorUsuarios import Flask, request
from flask_restful import Resource, Api
from .modelos import *
from .vistas import VistaUsuario,VistaLoginHistorical

app = create_app('default')
app_context = app.app_context()
app_context.push()
db.init_app(app)
db.create_all()

api = Api(app)
api.add_resource(VistaUsuario, '/usuario')
api.add_resource(VistaUsuario, '/loginhistory')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', ssl_context='adhoc')
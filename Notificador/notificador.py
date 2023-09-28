from celery import Celery
import datetime

celery_app= Celery(__name__, broker='redis://localhost:6379/0')

@celery_app.task(name='doble_autenticacion')
# Funcion registrar log recibe los parámetros y los guarda en un archivo separado por comas (csv)
def notificar_csv(usuario,canal,telefono,correo):
    # Obtener la fecha y hora actual en GMT-5
    fecha_hora_actual = datetime.datetime.now()
    
    # Crear una cadena con los nombres de las columnas
    nombres_columnas = "Fecha_Hora,mensaje,usuario,destino"

    # Verificar si el archivo ya existe, si no, crearlo e incluir los nombres de las columnas
    with open('notificador.csv', 'a+') as file:
        if file.tell() == 0:
            file.write(nombres_columnas + '\n')
        
        if canal == 'CORREO':
            canal_preferido = correo
        else:
            canal_preferido = telefono

        mensaje = "Se identifico actividad inusual en el inicio de sesión en el usuario {}, Se ha enviado un mensaje al {}: {}, confirme si es usted.".format(usuario,canal,canal_preferido)
        # Registrar los datos en el archivo CSV
        file.write(f'{fecha_hora_actual},{mensaje},{usuario},{canal_preferido}\n')
    
    return True
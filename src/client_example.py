import socket
import json
import datetime


def client (ip='172.18.1.200', port=80):
    datas = {  # Mensaje de datos a enviar
        'device_id': 1,
        'datos enviados': {
            'dato1': 'test',
            'dato2': 'test',
            'dato3': 'test'
        },
    }

    # Añadir el timestamp UTC al diccionario
    datas['timestamp'] = datetime.datetime.now(datetime.timezone.utc).strftime(
        '%Y-%m-%d %H:%M:%S')

    # Convertir el diccionario a una cadena JSON
    data_string = json.dumps(datas)

    # Creamos el socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Nos conectamos al servidor
        s.connect((ip, port))

        # Enviamos los datos
        s.send(data_string.encode('utf-8'))

        # Recibimos la respuesta
        data = s.recv(1024)
        print('Datos recibidos:', data)

client()

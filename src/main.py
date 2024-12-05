import gc
from time import sleep_ms
from Models.RpiPico import RpiPico
import usocket as socket
import ujson as json

# Importo variables de entorno
import env

# Habilito recolector de basura
gc.enable()

DEBUG = env.DEBUG

# Rpi Pico Model Instance
rpi = RpiPico(ssid=env.AP_NAME, password=env.AP_PASS, debug=DEBUG,
                     alternatives_ap=env.ALTERNATIVES_AP, hostname=env.HOSTNAME)

sleep_ms(100)

# Debug para mostrar el estado del wifi
rpi.wifi_debug()

# Pausa preventiva al desarrollar (ajustar, pero si usas dos hilos puede ahorrar tiempo por bloqueos de hardware ante errores)
sleep_ms(2000)

def handle_client(conn):
    """
    Procesa la recepción de datos.
    """

    conn.setblocking(False)
    conn.settimeout(5.0)  # wait for 5 seconds

    try:
        while True:
            data = conn.recv(1024)

            if data:
                data = data.decode('utf-8')

                if DEBUG:
                    print("Datos recibidos: ", data)

                data_dict = json.loads(data)

                # Respondemos al cliente, le devolvemos ok y los datos recibidos
                response = json.dumps({ 'status': 'ok', 'data': data_dict })
                conn.send(response.encode('utf-8'))

            else:
                conn.close()

                break

        conn.close()
    except Exception as e3:
        print("Error Websocket Server en handle_client(): ", e3)

def server():
    ip = "0.0.0.0"
    port = 80
    s = socket.socket()

    while True:
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((ip, port))
            s.listen(1)

            while True:
                try:
                    conn, addr = s.accept()

                    if DEBUG:
                        print('Conexión establecida con:', addr)

                    # Al existir cliente se maneja la conexión
                    handle_client(conn)
                except Exception as e1:
                    if DEBUG:
                        print('Error al ejecutar la escucha del servidor en start() dentro del while',e1)

        except Exception as e2:
            if DEBUG:
                print('Error al ejecutar la escucha del servidor en start()', e2)


def init ():
    """
    Primer hilo, flujo principal de la aplicación.
    En este hilo colocamos toda la lógica principal de funcionamiento.
    """

    if env.DEBUG:
        print('')
        print('Inicia hilo principal (thread0)')

    server()

    if env.DEBUG:
        print('')
        print('Termina el primer ciclo del hilo 0')
        print('')


while True:
    try:
        init()
    except Exception as e:
        if env.DEBUG:
            print('Error: ', e)
    finally:
        if env.DEBUG:
            print('Memoria antes de liberar: ', gc.mem_free())

        gc.collect()

        if env.DEBUG:
            print("Memoria después de liberar:", gc.mem_free())

        sleep_ms(5000)

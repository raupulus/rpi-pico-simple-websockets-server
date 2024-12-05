import gc
from time import sleep_ms

from machine import Pin

from Models.RpiPico import RpiPico
import usocket as socket
import ujson as json

# Importo variables de entorno
import env

# Habilito recolector de basura
gc.enable()

DEBUG = env.DEBUG

# Rpi Pico Model Instance
rpi: RpiPico = RpiPico(ssid=env.AP_NAME, password=env.AP_PASS, debug=DEBUG,
                       alternatives_ap=env.ALTERNATIVES_AP,
                       hostname=env.HOSTNAME)

led1 = Pin(2, Pin.OUT)
led2 = Pin(3, Pin.OUT)

sleep_ms(100)

# Debug para mostrar el estado del wifi
rpi.wifi_debug()

# Pausa preventiva al desarrollar (ajustar, pero si usas dos hilos puede ahorrar tiempo por bloqueos de hardware ante errores)
sleep_ms(2000)


def handle_client (conn: socket.socket) -> None:
    """
    Procesa la recepción de datos desde un cliente WebSocket.

    Recibe un mensaje en formato JSON, lo procesa, enciende o apaga el LED
    correspondiente según el contenido, y responde con un estado de éxito.

    Args:
        conn (socket.socket): La conexión con el cliente WebSocket.

    Returns:
        None
    """
    conn.setblocking(False)
    conn.settimeout(5.0)  # Espera por 5 segundos si no se recibe nada

    try:
        while True:
            data = conn.recv(1024)

            if data:
                data = data.decode('utf-8')

                if DEBUG:
                    print("Datos recibidos: ", data)

                # Procesar el JSON recibido
                data_dict = json.loads(data)

                # Verificar los datos y encender o apagar los LEDs
                action = data_dict.get("action")
                led = data_dict.get("led")

                if led == "integrated":
                    if action == "on":
                        rpi.led_on()
                    elif action == "off":
                        rpi.led_off()
                elif led == "1":
                    if action == "on":
                        led1.on()
                    elif action == "off":
                        led1.off()
                elif led == "2":
                    if action == "on":
                        led2.on()
                    elif action == "off":
                        led2.off()

                # Responder al cliente con un JSON de éxito
                response = json.dumps({ 'status': 'ok', 'data': data_dict })
                conn.send(response.encode('utf-8'))

            else:
                conn.close()
                break
        conn.close()

    except Exception as e3:
        print("Error en handle_client(): ", e3)


def server () -> None:
    """
    Función principal que crea el servidor WebSocket, espera por conexiones entrantes
    y maneja las solicitudes de los clientes.

    Este servidor escucha en la dirección 0.0.0.0 en el puerto 80 y acepta conexiones
    de clientes WebSocket.

    Returns:
        None
    """
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
                        print('Error en servidor durante accept():', e1)

        except Exception as e2:
            if DEBUG:
                print('Error al crear o escuchar el servidor en start():', e2)


def init () -> None:
    """
    Función inicial que arranca el servidor WebSocket y maneja el flujo de
    ejecución principal de la aplicación.

    Returns:
        None
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
            print('Error en el flujo principal:', e)
            print('Memoria antes de liberar: ', gc.mem_free())

        gc.collect()

        if env.DEBUG:
            print("Memoria después de liberar:", gc.mem_free())
    finally:
        sleep_ms(5000)

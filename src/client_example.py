import socket
import json
import sys
from typing import Optional


def client (ip: str = '172.18.1.200', port: int = 80, led: str = "integrated",
            action: str = "off") -> None:
    """
    Función que se conecta a un servidor WebSocket y envía un mensaje con el estado de un LED (encendido o apagado).

    Recibe el nombre del LED (integrado, 1, 2) y la acción (on, off), crea un mensaje JSON y lo envía al servidor.

    Args:
        ip (str): Dirección IP del servidor WebSocket (por defecto '172.18.1.200').
        port (int): Puerto en el que el servidor está escuchando (por defecto 80).
        led (str): El LED a controlar (puede ser 'integrated', '1', o '2').
        action (str): La acción a realizar ('on' o 'off').

    Returns:
        None
    """

    # Validar el parámetro 'action'
    if action not in ['on', 'off']:
        print(
            f"Error: La acción '{action}' no es válida. Debe ser 'on' o 'off'.")
        return

    # Crear el diccionario de datos a enviar
    data_dict = {
        'action': action,
        'led': led
    }

    # Convertir el diccionario a una cadena JSON
    data_string = json.dumps(data_dict)

    # Crear el socket para la conexión TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            # Conectarse al servidor
            s.connect((ip, port))

            # Enviar los datos al servidor
            s.send(data_string.encode('utf-8'))

            # Recibir la respuesta del servidor
            response = s.recv(1024)
            print(f"Datos recibidos: {response.decode('utf-8')}")

        except Exception as e:
            print(f"Error al conectar con el servidor: {e}")


def main () -> None:
    """
    Función principal que gestiona los argumentos de la línea de comandos y llama a la función `client` con los parámetros correspondientes.

    Los parámetros son:
    - led: El LED a controlar ('integrated', '1', '2').
    - action: La acción a realizar ('on' o 'off').

    Returns:
        None
    """

    # Comprobamos que se hayan pasado suficientes argumentos
    if len(sys.argv) != 3:
        print("Uso incorrecto. Debes especificar el LED y la acción.")
        print("Ejemplo de uso:")
        print("  python client_example.py integrated on")
        print("  python client_example.py 1 off")
        sys.exit(1)

    # Obtenemos los parámetros de la línea de comandos
    led = sys.argv[1]
    action = sys.argv[2]

    # Llamamos a la función client con los parámetros proporcionados
    client(led=led, action=action)


if __name__ == "__main__":
    main()

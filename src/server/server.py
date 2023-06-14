import base64
import json
import socket
import threading
import time

import requests
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

from src.common import encryption
from src.common.encryption import verify_message, generate_keys, get_public_key, get_private_key

# Generar par de claves RSA
generate_keys()
# Cargar la clave pública y privada del servidor
server_public_key = get_public_key()
server_private_key = get_private_key()

# Dirección IP y puerto del servidor
SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345

# Crear socket y enlazarlo a la dirección IP y puerto
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

# Lista para almacenar los hilos de los clientes
client_threads = []

# Lista par almacenar los sockets de los clientes y el nickname
# se guardarán en forma de tupla (socket, nickname)
client_sockets = []


def handle_client(client_socket):
    # Recibir el mensaje firmado del cliente
    data = client_socket.recv(2048)
    data = json.loads(base64.b64decode(data).decode())
    # Dividimos el mensaje
    nickname = data['message']['nickname']
    public_key = data['message']['public_key']
    signature = base64.b64decode(data['signature'])

    # Verificar la firma del mensaje utilizando la clave pública del cliente
    public_key = RSA.import_key(public_key)
    hash_value = SHA256.new(public_key.export_key())
    is_valid = verify_message(message=public_key.export_key(), signature=signature, public_key=public_key)

    if is_valid:  # Si la firma es válida guardamos el usuario en la base de datos
        # Guardamos el socket y el nickname del cliente
        client_sockets.append((client_socket, nickname))

        # Almacenar la clave pública del cliente en la base de datos a través de la API
        with requests.Session() as s:
            try:
                response = (s.post('http://127.0.0.1:5000/add_user', json={
                    'USERS': [
                        {
                            'NICKNAME': nickname,
                            'PUBLIC_KEY': public_key.export_key().decode()
                        }
                    ]
                }).text)
            except Exception as e:
                response = "ERROR: Error sending data to server: " + str(e)
        # Enviar respuesta al cliente
        if response in 'INFO: Users added successfully':
            # Creamos un json mensaje {nickname: str, public_key: public_key.export_key().decode()}
            message = {
                'nickname': 'SERVER',
                'public_key': server_public_key.export_key().decode()
            }
            # Firmamos el mensaje
            signature = encryption.sign_message(public_key.export_key(), server_private_key)
            data = {
                'message': message,
                'signature': base64.b64encode(signature).decode()
            }
            data = base64.b64encode(json.dumps(data).encode())
            client_socket.send(data)
            time.sleep(5)
            for client in client_sockets:
                client[0].send(f'[SERVER] {nickname} has joined the chatroom.'.encode())

            # Recibir mensajes del cliente
            while True:
                message = client_socket.recv(2048)
                print(message)
                # Descifrar el mensaje utilizando la clave privada del servidor
                message = encryption.decrypt_message(message, server_private_key)
                print(f'[{nickname}]: {message.decode()}')
                # Enviar mensaje a todos los clientes
                for client in client_sockets:
                    if client[0] != client_socket:
                        # Obtener la clave pública del cliente mediante la API
                        with requests.Session() as s:
                            try:
                                response = s.get('http://127.0.0.1:5000/publickey/' + client[1]).text
                                client_public_key = RSA.import_key(response)
                                message = encryption.encrypt_message(message, client_public_key)
                                print("mensaje a enviar", message)
                                client[0].send(f'[{nickname}]: {message}'.encode())
                            except Exception as e:
                                print("ERROR: Error sending data to server: " + str(e.with_traceback()))
    else:
        response = 'ERROR: Invalid signature.'
        client_socket.send(response.encode())

    # Cerrar conexión
    client_socket.close()


# Escuchar conexiones entrantes
server_socket.listen()
print('Esperando conexiones entrantes...')

try:
    while True:
        # Aceptar conexión de un cliente
        client_socket, client_address = server_socket.accept()
        print('Cliente conectado:', client_address)

        # Crear un hilo para manejar la conexión del cliente
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

        # Agregar el hilo a la lista de hilos de clientes
        client_threads.append(client_thread)


except KeyboardInterrupt:
    # Esperar a que todos los hilos de los clientes finalicen
    for client_thread in client_threads:
        client_thread.join()

    # Cerrar sockets
    server_socket.close()

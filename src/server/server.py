import base64
import json
import socket

import requests
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

from src.common.encryption import verify_message

# Dirección IP y puerto del servidor
SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345

# Crear socket y enlazarlo a la dirección IP y puerto
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

# Escuchar conexiones entrantes
server_socket.listen(1)
print('Esperando conexiones entrantes...')

# Aceptar conexión de un cliente
client_socket, client_address = server_socket.accept()
print('Cliente conectado:', client_address)

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
    print('Firma verificada.')
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
    client_socket.sendall(response.encode())
else:
    response = 'ERROR: Invalid signature.'
    client_socket.sendall(response.encode())

# Cerrar conexión
client_socket.close()
server_socket.close()

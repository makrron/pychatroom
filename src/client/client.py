import base64
import json
import socket
import threading

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

import src.common.encryption as encryption

# Dirección y puerto del servidor
SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 12345

# Generar par de claves RSA
encryption.generate_keys()
# Cargar clave pública y privada del usuario
public_key = encryption.get_public_key()
private_key = encryption.get_private_key()


# Función para recibir mensajes del servidor
def receive_messages():
    while True:
        # Recibir mensaje del servidor
        r = client_socket.recv(2048)
        # Descifrar el mensaje con la clave privada del cliente
        msg = encryption.decrypt_message(r, private_key)
        print(msg)


# Conectar al servidor
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_ADDRESS, SERVER_PORT))

# Enviar nickname y clave pública al servidor
nickname = input("Ingrese su nickname: ")
print("-" * 50)
message = {
    'nickname': nickname,
    'public_key': public_key.export_key().decode()
}

signature = encryption.sign_message(public_key.export_key(), private_key)
data = {
    'message': message,
    'signature': base64.b64encode(signature).decode()
}

# b64(json{'nickname':rsa(nick), 'public_key':firma(pkey)})
data = base64.b64encode(json.dumps(data).encode())
client_socket.send(data)

# Recibir respuesta del servidor
response = client_socket.recv(2048)
data = json.loads(base64.b64decode(data).decode())
# Dividimos el mensaje
server_nickname = data['message']['nickname']
server_public_key = data['message']['public_key']
server_signature = base64.b64decode(data['signature'])
# Verificar la firma del mensaje utilizando la clave pública del cliente
server_public_key = RSA.import_key(server_public_key)
hash_value = SHA256.new(server_public_key.export_key())
is_valid = encryption.verify_message(message=server_public_key.export_key(),
                                     signature=signature, public_key=server_public_key)

if is_valid:
    print('INFO: User added successfully')
    print('INFO: Joining chatroom...')
    response = client_socket.recv(2048)
    if 'joined the chatroom' in response.decode():
        print(response.decode())

        # Crear un hilo para recibir mensajes del servidor
        receive_thread = threading.Thread(target=receive_messages)
        receive_thread.start()

        # Enviar mensajes al servidor
        while True:
            # Obtener mensaje del usuario
            message = input()
            # cifrar el mensaje con la clave pública del servidor
            message = encryption.encrypt_message(message.encode(), server_public_key)
            client_socket.send(message)

    else:
        print(response.decode())
        client_socket.close()
        exit()

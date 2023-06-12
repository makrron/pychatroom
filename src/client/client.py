import base64
import json
import socket

from src.common.encryption import generate_keys, get_public_key, get_private_key, sign_message

# Dirección y puerto del servidor
SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 12345

# Generar par de claves RSA
generate_keys()
# Cargar clave pública y privada del usuario
public_key = get_public_key()
private_key = get_private_key()


# Conectar al servidor
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_ADDRESS, SERVER_PORT))

# Enviar nickname y clave pública al servidor
nickname = input("Ingrese su nickname: ")
message = {
    'nickname': nickname,
    'public_key': public_key.export_key().decode()
}

signature = sign_message(public_key.export_key(), private_key)
data = {
    'message': message,
    'signature': base64.b64encode(signature).decode()
}

# b64(json{'nickname':rsa(nick), 'public_key':firma(pkey)})
data = base64.b64encode(json.dumps(data).encode())
client_socket.send(data)

# Recibir respuesta del servidor
response = client_socket.recv(2048)
print(response.decode())


# Cerrar conexión
client_socket.close()

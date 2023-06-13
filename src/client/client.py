import base64
import json
import socket
import src.common.encryption as encryption

# Dirección y puerto del servidor
SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 12345

# Generar par de claves RSA
encryption.generate_keys()
# Cargar clave pública y privada del usuario
public_key = encryption.get_public_key()
private_key = encryption.get_private_key()

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
if 'joined the chatroom' in response.decode():
    print('INFO: User added successfully')
    print('INFO: Joining chatroom...')
    print(response.decode())
    while True:
        # Enviar mensaje al servidor
        message = input()
        client_socket.sendall(message.encode())
        # Recibir respuesta del servidor
        response = client_socket.recv(2048)
        print(response.decode())

else:
    print('esto?')
    client_socket.close()
    exit()

# pychatroom
Encrypted chat room using sockets 


- El directorio "pychatroom" es el directorio raíz del proyecto.
- El directorio "src" contiene todo el código fuente del proyecto.
- El directorio "client" contiene los archivos relacionados con el cliente del chat.
"client.py" es el archivo principal que contiene la lógica del cliente.
- El directorio "server" contiene los archivos relacionados con el servidor del chat.
"server.py" es el archivo principal que contiene la lógica del servidor.
- El directorio "api" contiene los archivos relacionados con la API del servidor.
    "api_chatroom.py" es el archivo que implementa la API del chatroom.
    "chatroom.db" es el archivo de base de datos SQLite que almacena los datos del chatroom.
- El directorio "common" contiene archivos compartidos entre el servidor y la API.
    "encryption.py" contiene funciones de utilidad relacionadas con la criptografía.



## DB Schema

```sql

create table USERS
(
    id         INTEGER      not null
        primary key autoincrement,
    nickname   varchar(128) not null
        unique,
    public_key varchar      not null
);

create table server_data
(
    public_key  varchar not null,
    private_key varchar not null
);
```

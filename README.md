# PyChatRoom
Encrypted RSA chat room using sockets 

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

#!/bin/bash
set -e

# Создаем директорию для сертификатов
mkdir -p ./certs

# Переходим в директорию с сертификатами
cd ./certs

# Генерируем приватный ключ для CA (Certificate Authority)
openssl genrsa -out ca.key 4096

# Создаем самоподписанный CA сертификат
openssl req -new -x509 -key ca.key -sha256 -subj "/C=RU/ST=Moscow/O=API Project/CN=API Project CA" -days 3650 -out ca.crt

# Генерируем приватные ключи для сервисов
openssl genrsa -out rest-api.key 2048
openssl genrsa -out graphql-api.key 2048
openssl genrsa -out grpc-api.key 2048

# Создаем CSR (Certificate Signing Request) для сервисов
openssl req -new -key rest-api.key -subj "/C=RU/ST=Moscow/O=API Project/CN=rest-api" -out rest-api.csr
openssl req -new -key graphql-api.key -subj "/C=RU/ST=Moscow/O=API Project/CN=graphql-api" -out graphql-api.csr
openssl req -new -key grpc-api.key -subj "/C=RU/ST=Moscow/O=API Project/CN=grpc-api" -out grpc-api.csr

# Создаем файл конфигурации для альтернативных имен
cat > ext.cnf << EOF
subjectAltName = @alt_names
[alt_names]
DNS.1 = localhost
DNS.2 = rest-api
DNS.3 = graphql-api
DNS.4 = grpc-api
IP.1 = 127.0.0.1
EOF

# Подписываем CSR с помощью CA
openssl x509 -req -in rest-api.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out rest-api.crt -days 825 -sha256 -extfile ext.cnf
openssl x509 -req -in graphql-api.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out graphql-api.crt -days 825 -sha256 -extfile ext.cnf
openssl x509 -req -in grpc-api.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out grpc-api.crt -days 825 -sha256 -extfile ext.cnf

# Объединяем сертификаты с приватными ключами для использования в серверах
cat rest-api.key rest-api.crt > rest-api.pem
cat graphql-api.key graphql-api.crt > graphql-api.pem
cat grpc-api.key grpc-api.crt > grpc-api.pem

echo "Сертификаты успешно созданы в директории ./certs"
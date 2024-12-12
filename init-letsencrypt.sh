#!/bin/bash

set -e

# Email for Let's Encrypt notifications
email="eraykahraman30@gmail.com"
domain="erayswe573.com.tr"
rsa_key_size=4096
data_path="./certbot"

echo "### Creating required directories ..."
mkdir -p "$data_path/conf/live/$domain"
mkdir -p "$data_path/www"

echo "### Setting proper permissions ..."
chmod -R 755 "$data_path"
chown -R $USER:$USER "$data_path"

echo "### Stopping existing containers if any ..."
docker compose down

echo "### Removing any existing certificates ..."
rm -rf "$data_path/conf/live/$domain"
rm -rf "$data_path/conf/archive/$domain"
rm -rf "$data_path/conf/renewal/$domain.conf"

echo "### Recreating certificate directories ..."
mkdir -p "$data_path/conf/live/$domain"
chmod -R 755 "$data_path/conf/live/$domain"

# Create a temporary self-signed certificate
echo "### Creating temporary self-signed certificate ..."
openssl req -x509 -nodes -newkey rsa:$rsa_key_size -days 1 \
    -keyout "$data_path/conf/live/$domain/privkey.pem" \
    -out "$data_path/conf/live/$domain/fullchain.pem" \
    -subj "/CN=localhost" || {
        echo "Failed to create self-signed certificate"
        exit 1
    }

echo "### Starting nginx ..."
docker compose up -d nginx
echo "### Waiting for nginx to start ..."
sleep 5

echo "### Requesting Let's Encrypt staging certificate ..."
docker compose run --rm --entrypoint "\
    certbot certonly --webroot -w /var/www/certbot \
    --email $email \
    -d $domain \
    --rsa-key-size $rsa_key_size \
    --agree-tos \
    --force-renewal \
    --staging \
    --non-interactive" certbot

echo "### Stopping nginx ..."
docker compose stop nginx

echo "### Requesting Let's Encrypt production certificate ..."
docker compose run --rm --entrypoint "\
    certbot certonly --webroot -w /var/www/certbot \
    --email $email \
    -d $domain \
    --rsa-key-size $rsa_key_size \
    --agree-tos \
    --force-renewal \
    --non-interactive" certbot

echo "### Starting nginx ..."
docker compose up -d nginx

echo "### Done! Certificate should now be installed."
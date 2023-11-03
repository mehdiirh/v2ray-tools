#!/bin/bash

bash <(curl -Ls https://raw.githubusercontent.com/vaxilu/x-ui/master/install.sh)

wget -O bbr.sh https://github.com/teddysun/across/raw/master/bbr.sh && chmod +x bbr.sh && bash bbr.sh
rm bbr.sh

echo
echo
echo

apt update && apt install nginx python3-certbot-nginx -y

echo
echo
echo

[[ -z "$server" ]] && echo -n "Enter server address: " && read -r server;

rm -rf /etc/nginx/sites-available/*
rm -rf /etc/nginx/sites-enabled/*

cd /etc/nginx/sites-available || exit 1
wget -O nginx-site.conf https://raw.githubusercontent.com/mehdiirh/v2ray-tools/master/nginx-site.conf

mv nginx-site.conf "$server"
sed -i "s/%HOST%/${server}/g" "$server"
ln -s /etc/nginx/sites-available/"$server" /etc/nginx/sites-enabled/

systemctl edit --full nginx
sed -i "s/worker_connections 768;/worker_connections 10000;/g"
sed -i "s/# multi_accept on;/multi_accept on;/g"

systemctl stop nginx
sudo certbot certonly --standalone --preferred-challenges http --agree-tos -d "$server"
systemctl restart nginx

cd ~ || exit 1

wget -O edit-db.py https://raw.githubusercontent.com/mehdiirh/v2ray-tools/master/edit-db.py
python3 edit-db.py "$server"

rm edit-db.py

x-ui restart

echo
echo "Done..."
echo

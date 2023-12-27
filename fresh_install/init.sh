#!/bin/bash

mkdir /var/log/v2ray

echo;
echo "Which panel do you want to install? ";
echo "1) X-UI";
echo "2) Sanaei";
echo "3) Alireza";
echo -n "Select an option: ";
read -r panel;
while true; do
  case $panel in
    1)
      bash <(curl -Ls https://raw.githubusercontent.com/vaxilu/x-ui/master/install.sh);
      break;
      ;;
    2)
      bash <(curl -Ls https://raw.githubusercontent.com/mhsanaei/3x-ui/master/install.sh)
      break;
      ;;
    3)
      bash <(curl -Ls https://raw.githubusercontent.com/alireza0/x-ui/master/install.sh)
      break;
      ;;
    *)
      echo -n "Invalid option. Please select a valid option (1, 2, or 3): ";
      read -r panel;
      ;;
  esac

done


wget -O bbr.sh --no-cache https://github.com/teddysun/across/raw/master/bbr.sh && chmod +x bbr.sh && bash bbr.sh
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
wget -O nginx-site.conf --no-cache https://raw.githubusercontent.com/mehdiirh/v2ray-tools/master/fresh_install/nginx-site.conf

mv nginx-site.conf "$server"
sed -i "s/%HOST%/${server}/g" "$server"
ln -s /etc/nginx/sites-available/"$server" /etc/nginx/sites-enabled/

sed -i '/KillMode=mixed/a LimitNOFILE=100000' /etc/systemd/system/nginx.service
sed -i "s/worker_connections 768;/worker_connections 10000;/g" /etc/nginx/nginx.conf
sed -i "s/# multi_accept on;/multi_accept on;/g" /etc/nginx/nginx.conf

systemctl stop nginx
sudo certbot certonly --standalone --preferred-challenges http --agree-tos -d "$server"
systemctl restart nginx

cd ~ || exit 1

x-ui stop

wget -O edit-db.py https://raw.githubusercontent.com/mehdiirh/v2ray-tools/master/fresh_install/edit-db.py
python3 edit-db.py "$server"
rm edit-db.py

x-ui restart

echo
echo "Done..."
echo

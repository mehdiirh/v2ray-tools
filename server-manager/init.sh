#!/usr/bin/bash

git clone https://github.com/mehdiirh/v2ray-tools
mv v2ray-tools/server-manager .
rm -rf v2ray-tools

cd server-manager || exit 1

apt-get install python3-venv -y

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

hexdump -vn16 -e'4/4 "%08X" 1 "\n"' /dev/urandom > token

cp systemd.service server-manager.service
sed -i "s|%WORKING_DIR%|$(pwd)|g" server-manager.service

mv server-manager.service /etc/systemd/system/

systemctl enable server-manager.service
systemctl restart server-manager.service
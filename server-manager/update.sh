#!/usr/bin/bash

git clone https://github.com/mehdiirh/v2ray-tools
mv v2ray-tools/server-manager/* .
rm -rf v2ray-tools

systemctl restart server-manager.service
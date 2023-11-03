import json
import os
import sqlite3
import sys

try:
    server = sys.argv[1]
except:
    server = input("Enter server domain: ")

XRAY_SETTINGS = json.dumps(
    {
        "log": {
            "access": "/var/log/v2ray/access.log",
            "error": "/var/log/v2ray/error.log",
            "loglevel": "warning"
        },
        "api": {
            "services": [
                "HandlerService",
                "LoggerService",
                "StatsService"
            ],
            "tag": "api"
        },
        "inbounds": [
            {
                "listen": "127.0.0.1",
                "port": 62789,
                "protocol": "dokodemo-door",
                "settings": {
                    "address": "127.0.0.1"
                },
                "tag": "api"
            }
        ],
        "outbounds": [
            {
                "protocol": "freedom",
                "settings": {}
            },
            {
                "protocol": "blackhole",
                "settings": {},
                "tag": "blocked"
            }
        ],
        "policy": {
            "system": {
                "statsInboundDownlink": True,
                "statsInboundUplink": True
            }
        },
        "routing": {
            "domainStrategy": "IPIfNonMatch",
            "rules": [
                {
                    "inboundTag": [
                        "api"
                    ],
                    "outboundTag": "api",
                    "type": "field"
                },
                {
                    "ip": [
                        "geoip:private"
                    ],
                    "outboundTag": "blocked",
                    "type": "field"
                },
                {
                    "type": "field",
                    "domain": [
                        "cshield",
                        "boostgram",
                        "shaparak",
                        "idpay",
                        "zibal",
                        "jibimo",
                        "payping",
                        "nextpay",
                        "cloudsuite",
                        "hexav.click",
                        "ipanel"
                    ],
                    "outboundTag": "direct",
                    "action": "none"
                },
                {
                    "type": "field",
                    "domain": [
                        "regexp:\\.ir$"
                    ],
                    "ip": [
                        "geoip:ir"
                    ],
                    "outboundTag": "blocked",
                    "action": "none"
                },
                {
                    "outboundTag": "blocked",
                    "protocol": [
                        "bittorrent"
                    ],
                    "type": "field"
                }
            ]
        },
        "stats": {}
    }
)


def yes_no_confirm(question: str) -> bool:
    while True:
        answer = input(question)

        if answer.lower() == "y":
            return True
        if answer.lower() == "n":
            return False
        else:
            sys.stdout.write("Wrong answer")


path = os.path.exists("/etc/x-ui/db")

path_confirm = True
if path:
    path_confirm = yes_no_confirm("DB found at [/etc/x-ui/x-ui.db]. do you confirm? [y/n] : ")

if not path or not path_confirm:
    while True:
        path = input("Enter DB path: ")
        if os.path.exists(path):
            break
        print(f"Path [{path}] does not exist.")

try:
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM inbounds;")  # Test connection
except sqlite3.OperationalError:
    print("Couldn't connect to database...")
    print("Exiting...")
    exit(1)
    raise


cursor.execute(
    "UPDATE settings SET settings.value = ? WHERE settings.key='xrayTemplateConfig'",
    (XRAY_SETTINGS,)
)

cursor.execute(
    "UPDATE settings SET settings.value=? WHERE settings.key='webCertFile'",
    (f"/etc/letsencrypt/live/{server}/fullchain.pem",)
)

cursor.execute(
    "UPDATE settings SET settings.value=? WHERE settings.key='webKeyFile'",
    (f"/etc/letsencrypt/live/{server}/privkey.pem",)
)

cursor.execute(
    "UPDATE settings SET settings.value=? WHERE settings.key='webPort'",
    (2053,)
)

if yes_no_confirm("Change admin password? [y/n]"):
    new_password = input('Enter New Password for user "admin": ')

    cursor.execute(
        "UPDATE users SET users.password=? WHERE users.username='admin'",
        (new_password,)
    )


connection.commit()
connection.close()

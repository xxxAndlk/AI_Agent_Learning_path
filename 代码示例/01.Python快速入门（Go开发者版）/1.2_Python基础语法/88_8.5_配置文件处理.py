import json
import configparser
from pathlib import Path

# JSON配置
config = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "myapp"
    },
    "debug": True
}

# 读取JSON配置
with open("config.json", "w") as f:
    json.dump(config, f, indent=2)

with open("config.json") as f:
    config = json.load(f)

# INI配置文件
parser = configparser.ConfigParser()
parser.read("settings.ini")

database_host = parser.get("database", "host")

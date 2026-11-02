#!/usr/bin/env python3
"""Consulta las interfaces de un router MikroTik."""

import json
import os
import sys
from netmiko import ConnectHandler


def main():
    required = ["MT_HOST", "MT_USER", "MT_PASS"]
    missing = [key for key in required if not os.getenv(key)]

    if missing:
        print(json.dumps({
            "success": False,
            "error": f"Faltan variables: {', '.join(missing)}"
        }, ensure_ascii=False))
        sys.exit(1)

    device = {
        "device_type": "mikrotik_routeros",
        "host": os.environ["MT_HOST"],
        "username": os.environ["MT_USER"],
        "password": os.environ["MT_PASS"],
        "port": int(os.getenv("MT_PORT", "22")),
        "timeout": 15,
        "conn_timeout": 15,
    }

    try:
        with ConnectHandler(**device) as connection:
            result = connection.send_command("/interface print")

        print(json.dumps({
            "success": True,
            "tool": "consultar_interfaces",
            "data": result
        }, ensure_ascii=False, indent=2))

    except Exception as error:
        print(json.dumps({
            "success": False,
            "tool": "consultar_interfaces",
            "error": str(error)
        }, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()

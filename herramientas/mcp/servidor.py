

#!/usr/bin/env python3
"""Servidor MCP para consultas de MikroTik."""

import json
import os
import subprocess
import sys
from pathlib import Path
from mcp.server.fastmcp import FastMCP

RAIZ = Path(__file__).resolve().parents[2]
PYTHON_TOOLS = RAIZ / "herramientas" / "python"

mcp = FastMCP("mikrotik")


def cargar_entorno():
    entorno = os.environ.copy()
    archivo = RAIZ / ".env"

    if archivo.exists():
        for linea in archivo.read_text().splitlines():
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            clave, _, valor = linea.partition("=")
            entorno[clave.strip()] = valor.strip().strip('"').strip("'")

    return entorno



def ejecutar(nombre: str) -> dict:
    permitidas = {
        "consultar_interfaces.py",
        "consultar_direcciones_ip.py",
    }

    if nombre not in permitidas:
        return {"success": False, "error": "Herramienta no autorizada"}

    try:
        resultado = subprocess.run(
            [sys.executable, str(PYTHON_TOOLS / nombre)],
            cwd=str(RAIZ),
            env=cargar_entorno(),
            capture_output=True,
            text=True,
            timeout=30,
        )

        try:
            datos = json.loads(resultado.stdout)
            return datos
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "No se recibió JSON válido",
                "codigo_salida": resultado.returncode,
                "stderr": resultado.stderr.strip(),
                "stdout": resultado.stdout.strip(),
            }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Tiempo de espera agotado"}
    except Exception as error:
        return {"success": False, "error": str(error)}


def consultar_interfaces() -> dict:
    """Consulta interfaces y estados del MikroTik."""
    return ejecutar("consultar_interfaces.py")


@mcp.tool()
def consultar_direcciones_ip() -> dict:
    """Consulta las direcciones IP del MikroTik."""
    return ejecutar("consultar_direcciones_ip.py")


if __name__ == "__main__":
    mcp.run(transport="stdio")

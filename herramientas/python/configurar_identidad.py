#!/usr/bin/env python3
"""Modifica la identidad (nombre) de un router MikroTik de forma controlada.

Flujo:
    1. Valida el nombre solicitado.
    2. Consulta la identidad actual del router.
    3. Si ya coincide, no realiza cambios.
    4. Solicita confirmación al operador antes de modificar.
    5. Aplica el cambio.
    6. Verifica, en una conexión nueva, que el cambio se haya aplicado.

El resultado se imprime en formato JSON por la salida estándar. Los mensajes
para el operador (plan y confirmación) se muestran por la salida de errores,
para que la salida estándar contenga solamente el JSON.

Uso:
    python herramientas/python/configurar_identidad.py --nombre Hermes-CHR
    python herramientas/python/configurar_identidad.py --nombre Hermes-CHR --confirmar

Códigos de salida:
    0  cambio aplicado y verificado, o no era necesario modificar
    1  error de validación, conexión o verificación
    2  el operador no confirmó el cambio
"""

import argparse
import json
import os
import re
import sys
from netmiko import ConnectHandler

TOOL = "configurar_identidad"
NOMBRE_VALIDO = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
RESPUESTAS_AFIRMATIVAS = {"s", "si", "sí"}
ERROR_ROUTEROS = re.compile(
    r"failure:|syntax error|expected end of command|bad command name|invalid value",
    re.IGNORECASE)


def responder(codigo, **datos):
    """Imprime el resultado en JSON y finaliza con el código indicado."""
    print(json.dumps({"tool": TOOL, **datos}, ensure_ascii=False, indent=2))
    sys.exit(codigo)


def obtener_dispositivo():
    required = ["MT_HOST", "MT_USER", "MT_PASS"]
    missing = [key for key in required if not os.getenv(key)]

    if missing:
        responder(1, success=False, estado="error",
                  error=f"Faltan variables: {', '.join(missing)}")

    return {
        "device_type": "mikrotik_routeros",
        "host": os.environ["MT_HOST"],
        "username": os.environ["MT_USER"],
        "password": os.environ["MT_PASS"],
        "port": int(os.getenv("MT_PORT", "22")),
        "timeout": 15,
        "conn_timeout": 15,
    }


def leer_identidad(device):
    """Consulta la identidad actual en una conexión independiente."""
    with ConnectHandler(**device) as connection:
        salida = connection.send_command("/system identity print")

    coincidencia = re.search(r"name:\s*(\S.*)", salida)
    if not coincidencia:
        raise RuntimeError(f"No se pudo interpretar la identidad: {salida!r}")
    return coincidencia.group(1).strip()


def aplicar_identidad(device, nombre):
    """Aplica la nueva identidad.

    Al cambiar la identidad también cambia el prompt de RouterOS
    ([usuario@identidad] >), por lo que se espera cualquier prompt de
    RouterOS en lugar del prompt detectado al conectar.
    """
    with ConnectHandler(**device) as connection:
        salida = connection.send_command(
            f'/system identity set name="{nombre}"',
            expect_string=r"\]\s*>",
        )

    if ERROR_ROUTEROS.search(salida):
        raise RuntimeError(f"RouterOS rechazó el cambio: {salida.strip()}")


def solicitar_confirmacion(actual, nuevo):
    print("Cambio solicitado sobre el MikroTik:", file=sys.stderr)
    print(f"  Identidad actual: {actual}", file=sys.stderr)
    print(f"  Identidad nueva:  {nuevo}", file=sys.stderr)
    print("¿Confirma el cambio? [s/N]: ", end="", file=sys.stderr, flush=True)

    respuesta = sys.stdin.readline()
    if not respuesta:
        print("", file=sys.stderr)
    return respuesta.strip().lower() in RESPUESTAS_AFIRMATIVAS


def main():
    parser = argparse.ArgumentParser(
        description="Modifica la identidad de un router MikroTik con "
                    "comprobación previa, confirmación y verificación.")
    parser.add_argument("--nombre", required=True,
                        help="Nueva identidad del router (letras, números, '.', '_' o '-').")
    parser.add_argument("--confirmar", action="store_true",
                        help="Indica que el operador ya confirmó el cambio y omite la pregunta.")
    args = parser.parse_args()

    nombre = args.nombre.strip()
    if not NOMBRE_VALIDO.match(nombre):
        responder(1, success=False, estado="error", identidad_solicitada=nombre,
                  error="Nombre no válido: use de 1 a 64 caracteres entre "
                        "letras, números, '.', '_' o '-'.")

    device = obtener_dispositivo()

    # 1. Comprobación del estado actual
    try:
        actual = leer_identidad(device)
    except Exception as error:
        responder(1, success=False, estado="error", identidad_solicitada=nombre,
                  error=f"No se pudo consultar la identidad actual: {error}")

    if actual == nombre:
        responder(0, success=True, estado="sin_cambios",
                  identidad_anterior=actual, identidad_solicitada=nombre,
                  identidad_final=actual, cambio_aplicado=False, verificado=True,
                  mensaje="El router ya tiene la identidad solicitada; no se realizaron cambios.")

    # 2. Confirmación del operador
    if not args.confirmar and not solicitar_confirmacion(actual, nombre):
        responder(2, success=False, estado="cancelado",
                  identidad_anterior=actual, identidad_solicitada=nombre,
                  identidad_final=actual, cambio_aplicado=False, verificado=False,
                  mensaje="El operador no confirmó el cambio; no se modificó el router.")

    # 3. Aplicación del cambio
    try:
        aplicar_identidad(device, nombre)
    except Exception as error:
        responder(1, success=False, estado="error",
                  identidad_anterior=actual, identidad_solicitada=nombre,
                  error=f"No se pudo aplicar el cambio: {error}")

    # 4. Verificación en una conexión nueva
    try:
        final = leer_identidad(device)
    except Exception as error:
        responder(1, success=False, estado="error",
                  identidad_anterior=actual, identidad_solicitada=nombre,
                  cambio_aplicado=True, verificado=False,
                  error=f"El cambio se envió, pero no se pudo verificar: {error}")

    if final != nombre:
        responder(1, success=False, estado="error",
                  identidad_anterior=actual, identidad_solicitada=nombre,
                  identidad_final=final, cambio_aplicado=True, verificado=False,
                  error="La identidad final no coincide con la solicitada.")

    responder(0, success=True, estado="aplicado",
              identidad_anterior=actual, identidad_solicitada=nombre,
              identidad_final=final, cambio_aplicado=True, verificado=True,
              mensaje="Identidad modificada y verificada correctamente.")


if __name__ == "__main__":
    main()

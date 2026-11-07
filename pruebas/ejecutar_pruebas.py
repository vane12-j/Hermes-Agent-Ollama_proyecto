#!/usr/bin/env python3
"""Pruebas de funcionamiento de las herramientas del proyecto.

Ejecuta contra un MikroTik real las cuatro herramientas:

    1. consultar_interfaces.py      (Python, consulta)
    2. consultar_direcciones_ip.py  (Python, consulta)
    3. configurar_identidad.py      (Python, modificación)
    4. Playbooks de Ansible         (status, config y validation)

Cada caso guarda su evidencia (comando, código de salida y salidas) en
pruebas/evidencias/ y al final se genera pruebas/evidencias/resumen.md.

La identidad original del router se restaura al terminar.

Uso (desde la raíz del proyecto, con el entorno virtual activo):
    python pruebas/ejecutar_pruebas.py
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EVIDENCIAS = RAIZ / "pruebas" / "evidencias"
PYTHON = sys.executable
HERRAMIENTAS = RAIZ / "herramientas" / "python"
INVENTARIO = "herramientas/ansible/inventory/hosts.yml"
PLAYBOOKS = "herramientas/ansible/playbooks"
ANSIBLE_VENV = Path(sys.executable).parent / "ansible-playbook"
ANSIBLE_PLAYBOOK = os.getenv("ANSIBLE_PLAYBOOK",
                             str(ANSIBLE_VENV) if ANSIBLE_VENV.exists() else "ansible-playbook")
NOMBRE_PRUEBA = "Hermes-Prueba"

resultados = []


def cargar_env():
    """Carga .env si las variables del MikroTik no están definidas."""
    archivo = RAIZ / ".env"
    if os.getenv("MT_HOST") or not archivo.exists():
        return
    for linea in archivo.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if linea and not linea.startswith("#") and "=" in linea:
            clave, valor = linea.split("=", 1)
            os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


def ocultar(texto):
    clave = os.getenv("MT_PASS")
    return texto.replace(clave, "********") if clave else texto


def ejecutar(cmd, entrada=""):
    # RouterOS cierra la conexión si paramiko ofrece primero llaves SSH locales
    # (~/.ssh/id_*) que el router no conoce; Ansible debe usar solo la contraseña.
    env = {"ANSIBLE_PARAMIKO_LOOK_FOR_KEYS": "False", **os.environ,
           "ANSIBLE_NOCOLOR": "1", "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(cmd, cwd=RAIZ, input=entrada, capture_output=True,
                          text=True, env=env, timeout=300)


def guardar_evidencia(numero, nombre, cmd, entrada, proceso):
    archivo = EVIDENCIAS / f"{numero:02d}_{nombre}.txt"
    contenido = [
        f"Fecha: {datetime.now():%Y-%m-%d %H:%M:%S}",
        f"Comando: {' '.join(str(c) for c in cmd).replace(str(RAIZ) + os.sep, '')}",
    ]
    if entrada:
        contenido.append(f"Entrada del operador: {entrada.strip()!r}")
    contenido += [
        f"Código de salida: {proceso.returncode}",
        "",
        "----- salida estándar -----",
        proceso.stdout.rstrip(),
        "",
        "----- salida de errores -----",
        proceso.stderr.rstrip(),
        "",
    ]
    archivo.write_text(ocultar("\n".join(contenido)), encoding="utf-8")
    return archivo.name


def caso(herramienta, nombre, descripcion, cmd, entrada, validar):
    """Ejecuta un caso, guarda la evidencia y registra el resultado."""
    numero = len(resultados) + 1
    proceso = ejecutar(cmd, entrada)
    evidencia = guardar_evidencia(numero, nombre, cmd, entrada, proceso)

    try:
        datos = json.loads(proceso.stdout)
    except ValueError:
        datos = None

    try:
        correcto, detalle = validar(proceso, datos)
    except Exception as error:
        correcto, detalle = False, f"Error al validar: {error}"

    resultados.append({
        "numero": numero, "herramienta": herramienta, "descripcion": descripcion,
        "correcto": correcto, "detalle": detalle, "evidencia": evidencia,
    })
    print(f"[{'PASA' if correcto else 'FALLA'}] {numero:02d} {herramienta}: {descripcion} - {detalle}")
    return datos


def identidad(*args):
    return [PYTHON, str(HERRAMIENTAS / "configurar_identidad.py"), *args]


def playbook(nombre, *args):
    return [ANSIBLE_PLAYBOOK, "-i", INVENTARIO, f"{PLAYBOOKS}/{nombre}", *args]


def recap(salida):
    """Devuelve la línea PLAY RECAP del router."""
    for linea in salida.splitlines():
        if linea.startswith("router") and "ok=" in linea:
            return " ".join(linea.split())
    return "sin PLAY RECAP"


def probar_consultas():
    host = os.getenv("MT_HOST", "")

    caso("consultar_interfaces", "consultar_interfaces",
         "Lista las interfaces del router",
         [PYTHON, str(HERRAMIENTAS / "consultar_interfaces.py")], "",
         lambda p, d: (p.returncode == 0 and d["success"] and "ether1" in d["data"],
                       "success=true, aparece ether1" if p.returncode == 0
                       else d and d.get("error")))

    caso("consultar_direcciones_ip", "consultar_direcciones_ip",
         "Lista las direcciones IP del router",
         [PYTHON, str(HERRAMIENTAS / "consultar_direcciones_ip.py")], "",
         lambda p, d: (p.returncode == 0 and d["success"] and host in d["data"],
                       f"success=true, aparece {host}" if p.returncode == 0
                       else d and d.get("error")))


def probar_configurar_identidad():
    """Devuelve la identidad original del router, o None si no se obtuvo."""
    tool = "configurar_identidad"

    caso(tool, "identidad_nombre_invalido",
         "Rechaza un nombre no válido sin conectarse",
         identidad("--nombre", "mal;nombre"), "",
         lambda p, d: (p.returncode == 1 and d["estado"] == "error"
                       and "no válido" in d["error"], d["error"]))

    datos = caso(tool, "identidad_operador_rechaza",
                 "Consulta el estado actual y el operador rechaza el cambio",
                 identidad("--nombre", NOMBRE_PRUEBA), "n\n",
                 lambda p, d: (p.returncode == 2 and d["estado"] == "cancelado"
                               and not d["cambio_aplicado"] and "¿Confirma" in p.stderr,
                               f"actual={d.get('identidad_anterior')}, estado={d['estado']}"))
    original = (datos or {}).get("identidad_anterior")
    if not original:
        print("No se obtuvo la identidad original; se omiten las pruebas que modifican el router.")
        return None

    caso(tool, "identidad_sin_respuesta",
         "Sin respuesta del operador (sin terminal) no se modifica",
         identidad("--nombre", NOMBRE_PRUEBA), "",
         lambda p, d: (p.returncode == 2 and d["estado"] == "cancelado"
                       and not d["cambio_aplicado"], f"estado={d['estado']}"))

    caso(tool, "identidad_sin_cambios_tras_rechazo",
         "La identidad sigue siendo la original tras los rechazos",
         identidad("--nombre", original), "",
         lambda p, d: (p.returncode == 0 and d["estado"] == "sin_cambios"
                       and d["identidad_final"] == original,
                       f"identidad={d.get('identidad_final')}, estado={d['estado']}"))

    caso(tool, "identidad_operador_confirma",
         "El operador confirma, se aplica y se verifica el cambio",
         identidad("--nombre", NOMBRE_PRUEBA), "s\n",
         lambda p, d: (p.returncode == 0 and d["estado"] == "aplicado" and d["verificado"]
                       and d["identidad_final"] == NOMBRE_PRUEBA,
                       f"{d.get('identidad_anterior')} -> {d.get('identidad_final')}, "
                       f"verificado={d.get('verificado')}"))

    caso(tool, "identidad_idempotencia",
         "Repetir el mismo nombre no modifica ni pide confirmación",
         identidad("--nombre", NOMBRE_PRUEBA), "",
         lambda p, d: (p.returncode == 0 and d["estado"] == "sin_cambios"
                       and not d["cambio_aplicado"] and "¿Confirma" not in p.stderr,
                       f"estado={d['estado']}, cambio_aplicado={d['cambio_aplicado']}"))

    restaurar_identidad(original, "Restaura la identidad original con --confirmar")
    return original


def restaurar_identidad(original, descripcion):
    caso("configurar_identidad", "identidad_restaurar", descripcion,
         identidad("--nombre", original, "--confirmar"), "",
         lambda p, d: (p.returncode == 0 and d["identidad_final"] == original
                       and d["verificado"],
                       f"identidad={d.get('identidad_final')}, estado={d['estado']}"))


def probar_ansible(original):
    tool = "ansible"

    for nombre in ("router_status.yml", "router_config.yml", "router_validation.yml"):
        caso(tool, f"ansible_sintaxis_{nombre.removesuffix('.yml')}",
             f"Validación de sintaxis de {nombre}",
             playbook(nombre, "--syntax-check"), "",
             lambda p, d: (p.returncode == 0, f"código de salida {p.returncode}"))

    caso(tool, "ansible_router_status", "Consulta de identidad y recursos (router_status.yml)",
         playbook("router_status.yml"), "",
         lambda p, d: (p.returncode == 0 and "failed=0" in recap(p.stdout)
                       and "name:" in p.stdout, recap(p.stdout)))

    caso(tool, "ansible_router_validation_1", "Primera ejecución de router_validation.yml",
         playbook("router_validation.yml"), "",
         lambda p, d: (p.returncode == 0 and "failed=0" in recap(p.stdout), recap(p.stdout)))

    caso(tool, "ansible_router_validation_2",
         "Segunda ejecución de router_validation.yml (idempotencia)",
         playbook("router_validation.yml"), "",
         lambda p, d: (p.returncode == 0 and "changed=0" in recap(p.stdout)
                       and "failed=0" in recap(p.stdout), recap(p.stdout)))

    if original:
        restaurar_identidad(original, "Restaura la identidad original tras las pruebas de Ansible")


def version(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True).stdout.splitlines()[0]
    except (OSError, IndexError):
        return "no disponible"


def escribir_resumen(inicio):
    aprobadas = sum(r["correcto"] for r in resultados)
    lineas = [
        "# Resumen de pruebas de funcionamiento",
        "",
        f"- Fecha: {inicio:%Y-%m-%d %H:%M:%S}",
        f"- Router: {os.getenv('MT_HOST')}:{os.getenv('MT_PORT', '22')} (usuario {os.getenv('MT_USER')})",
        f"- Python: {platform.python_version()} | Ansible: {version([ANSIBLE_PLAYBOOK, '--version'])}",
        f"- Resultado: **{aprobadas} de {len(resultados)} casos correctos**",
        "",
        "| # | Herramienta | Caso | Resultado | Detalle | Evidencia |",
        "|---|---|---|---|---|---|",
    ]
    for r in resultados:
        detalle = str(r["detalle"]).replace("|", "\\|")
        lineas.append(f"| {r['numero']:02d} | {r['herramienta']} | {r['descripcion']} | "
                      f"{'PASA' if r['correcto'] else 'FALLA'} | {detalle} | "
                      f"[{r['evidencia']}]({r['evidencia']}) |")
    (EVIDENCIAS / "resumen.md").write_text(ocultar("\n".join(lineas) + "\n"), encoding="utf-8")
    return aprobadas


def main():
    cargar_env()
    faltantes = [v for v in ("MT_HOST", "MT_USER", "MT_PASS") if not os.getenv(v)]
    if faltantes:
        sys.exit(f"Faltan variables: {', '.join(faltantes)} (configure .env)")
    if not shutil.which(ANSIBLE_PLAYBOOK):
        sys.exit(f"No se encontró {ANSIBLE_PLAYBOOK}; instale Ansible.")

    EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    for viejo in EVIDENCIAS.glob("*.txt"):
        viejo.unlink()

    inicio = datetime.now()
    probar_consultas()
    original = probar_configurar_identidad()
    probar_ansible(original)

    aprobadas = escribir_resumen(inicio)
    print(f"\n{aprobadas} de {len(resultados)} casos correctos. "
          f"Evidencias en {EVIDENCIAS.relative_to(RAIZ)}/")
    sys.exit(0 if aprobadas == len(resultados) else 1)


if __name__ == "__main__":
    main()

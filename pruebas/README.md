# Pruebas de funcionamiento de las herramientas

## 1. Objetivo

Comprobar, contra un router MikroTik real, el funcionamiento de las cuatro herramientas del proyecto:

| # | Herramienta | Tipo | Archivo |
|---|---|---|---|
| 1 | Consultar interfaces | Python (consulta) | `herramientas/python/consultar_interfaces.py` |
| 2 | Consultar direcciones IP | Python (consulta) | `herramientas/python/consultar_direcciones_ip.py` |
| 3 | Configurar identidad | Python (modificación) | `herramientas/python/configurar_identidad.py` |
| 4 | Playbooks de Ansible | Ansible | `herramientas/ansible/playbooks/*.yml` |

Las pruebas se ejecutan de forma automática con `pruebas/ejecutar_pruebas.py`. Cada caso guarda su evidencia en `pruebas/evidencias/` y al final se genera el resumen `pruebas/evidencias/resumen.md`.

## 2. Entorno de pruebas

| Componente | Versión |
|---|---|
| Sistema de administración | Debian 13 |
| Python | 3.13.5 |
| Netmiko / Paramiko (entorno virtual) | 4.8.0 / 5.1.0 |
| Ansible Core (paquete de Debian) | 2.19.11 |
| Paramiko del sistema (`python3-paramiko`) | 3.5.1 |
| `community.routeros` / `ansible.netcommon` | 3.10.0 / 8.1.0 |
| GNS3 | 3.0.6 |
| MikroTik CHR | RouterOS 7.16 (`chr-7.16.img`) |

### Topología

```text
Debian (tap0 192.168.100.1/24) ── Cloud1 [tap0] ── [ether1] MikroTik CHR (192.168.100.2/24)
```

- Proyecto GNS3: `HermesMikroTik`.
- Usuario del router: `admin` (grupo `full`), SSH en el puerto 22.
- Identidad inicial del router: `MikroTik`.

## 3. Requisitos previos

1. Router encendido, con SSH habilitado y conectividad desde Debian (`ping 192.168.100.2`).
2. Archivo `.env` en la raíz del proyecto con `MT_HOST`, `MT_USER`, `MT_PASS` y `MT_PORT` (ver la sección 8 del README principal).
3. Entorno virtual con las dependencias instaladas: `pip install -r requirements.txt`.
4. Ansible con las colecciones `community.routeros` y `ansible.netcommon`, y Paramiko disponible para el Python que ejecuta Ansible.
5. La llave SSH del router registrada en `~/.ssh/known_hosts`, por ejemplo conectándose una vez con `ssh admin@192.168.100.2`.

## 4. Ejecución

Desde la raíz del proyecto:

```bash
source .venv/bin/activate
python pruebas/ejecutar_pruebas.py
```

Si las variables `MT_*` no están cargadas en la terminal, el script las lee del archivo `.env`.

El script usa el `ansible-playbook` del entorno virtual si existe y, si no, el del sistema. Se puede indicar otro con la variable `ANSIBLE_PLAYBOOK`.

La contraseña del router nunca se escribe en las evidencias: se reemplaza por `********`.

Al terminar, el router queda con su identidad original. Los playbooks de Ansible dejan en `ether1` el comentario `Gestion Ansible - TAP`, que es el valor deseado definido por ellos.

## 5. Casos de prueba

| # | Herramienta | Caso | Resultado esperado |
|---|---|---|---|
| 01 | consultar_interfaces | Listar las interfaces | `success: true` y aparece `ether1` |
| 02 | consultar_direcciones_ip | Listar las direcciones IP | `success: true` y aparece `MT_HOST` |
| 03 | configurar_identidad | Nombre no válido (`mal;nombre`) | Rechazado sin conectarse al router (código 1) |
| 04 | configurar_identidad | Consulta del estado actual y el operador responde `n` | `cancelado`, sin cambios (código 2) |
| 05 | configurar_identidad | Sin respuesta del operador (ejecución sin terminal) | `cancelado`, sin cambios (código 2) |
| 06 | configurar_identidad | Comprobar que la identidad no cambió | `sin_cambios`, identidad original |
| 07 | configurar_identidad | El operador responde `s` | `aplicado` y `verificado: true` |
| 08 | configurar_identidad | Repetir el mismo nombre | `sin_cambios`, no pide confirmación |
| 09 | configurar_identidad | Restaurar la identidad original con `--confirmar` | `aplicado` y `verificado: true` |
| 10-12 | Ansible | `--syntax-check` de los tres playbooks | Código de salida 0 |
| 13 | Ansible | Ejecutar `router_status.yml` | `failed=0` y se muestra la identidad |
| 14 | Ansible | Primera ejecución de `router_validation.yml` | `failed=0` (corrige identidad y comentario) |
| 15 | Ansible | Segunda ejecución de `router_validation.yml` | `changed=0` y `failed=0` (idempotencia) |
| 16 | configurar_identidad | Restaurar la identidad original después de Ansible | Identidad original verificada |

## 6. Resultados

Ejecución del 6 de noviembre de 2026: **16 de 16 casos correctos**.

| # | Herramienta | Caso | Resultado | Detalle |
|---|---|---|---|---|
| 01 | consultar_interfaces | Listar las interfaces | PASA | `success=true`, aparece `ether1` |
| 02 | consultar_direcciones_ip | Listar las direcciones IP | PASA | `success=true`, aparece `192.168.100.2` |
| 03 | configurar_identidad | Nombre no válido | PASA | Rechazado: "Nombre no válido" |
| 04 | configurar_identidad | El operador rechaza el cambio | PASA | Identidad actual `MikroTik`, `cancelado` |
| 05 | configurar_identidad | Sin respuesta del operador | PASA | `cancelado` |
| 06 | configurar_identidad | La identidad no cambió | PASA | `MikroTik`, `sin_cambios` |
| 07 | configurar_identidad | El operador confirma el cambio | PASA | `MikroTik -> Hermes-Prueba`, `verificado=true` |
| 08 | configurar_identidad | Idempotencia | PASA | `sin_cambios`, `cambio_aplicado=false` |
| 09 | configurar_identidad | Restaurar la identidad | PASA | `MikroTik`, `aplicado` |
| 10 | Ansible | Sintaxis de `router_status.yml` | PASA | Código de salida 0 |
| 11 | Ansible | Sintaxis de `router_config.yml` | PASA | Código de salida 0 |
| 12 | Ansible | Sintaxis de `router_validation.yml` | PASA | Código de salida 0 |
| 13 | Ansible | `router_status.yml` | PASA | `ok=4 changed=0 failed=0` |
| 14 | Ansible | `router_validation.yml` (1.ª ejecución) | PASA | `ok=8 changed=2 failed=0` |
| 15 | Ansible | `router_validation.yml` (2.ª ejecución) | PASA | `ok=6 changed=0 failed=0 skipped=2` |
| 16 | configurar_identidad | Restaurar la identidad después de Ansible | PASA | `MikroTik`, `aplicado` |

El detalle completo de cada caso (comando, entrada del operador, código de salida y salidas) está en [`evidencias/`](evidencias/), y el resumen generado por el script en [`evidencias/resumen.md`](evidencias/resumen.md).

## 7. Evidencias destacadas

### Confirmación del operador y verificación (caso 07)

El operador ve el cambio solicitado antes de aplicarlo:

```text
Cambio solicitado sobre el MikroTik:
  Identidad actual: MikroTik
  Identidad nueva:  Hermes-Prueba
¿Confirma el cambio? [s/N]:
```

Con la respuesta `s`, la herramienta aplica el cambio y lo verifica en una conexión nueva:

```json
{
  "tool": "configurar_identidad",
  "success": true,
  "estado": "aplicado",
  "identidad_anterior": "MikroTik",
  "identidad_solicitada": "Hermes-Prueba",
  "identidad_final": "Hermes-Prueba",
  "cambio_aplicado": true,
  "verificado": true,
  "mensaje": "Identidad modificada y verificada correctamente."
}
```

El registro del router (`/log print`) confirma el cambio. El sufijo `+ct511w4098h` lo agrega Netmiko al usuario para configurar la terminal:

```text
system,info system identity changed by ssh:admin+ct511w4098h@192.168.100.1 (/system identity set name=Hermes-Prueba)
```

### Rechazo del operador (caso 04)

```json
{
  "tool": "configurar_identidad",
  "success": false,
  "estado": "cancelado",
  "identidad_anterior": "MikroTik",
  "identidad_solicitada": "Hermes-Prueba",
  "identidad_final": "MikroTik",
  "cambio_aplicado": false,
  "verificado": false,
  "mensaje": "El operador no confirmó el cambio; no se modificó el router."
}
```

### Idempotencia de la herramienta Python (caso 08)

Al pedir la identidad que el router ya tiene, la herramienta responde `"estado": "sin_cambios"` sin pedir confirmación ni enviar comandos de modificación.

### Idempotencia de Ansible (caso 15)

En la segunda ejecución de `router_validation.yml` se omiten las dos tareas de corrección y las aserciones pasan:

Extracto de `evidencias/15_ansible_router_validation_2.txt`:

```text
TASK [Corregir identidad si es necesario] **************************************
skipping: [router]
TASK [Corregir comentario si es necesario] *************************************
skipping: [router]
TASK [Validar identidad configurada] *******************************************
    "msg": "La identidad del MikroTik es correcta."
TASK [Validar comentario de interfaz] ******************************************
    "msg": "El comentario de ether1 es correcto."
router                     : ok=6    changed=0    unreachable=0    failed=0    skipped=2    rescued=0    ignored=0
```

## 8. Observaciones y problemas encontrados

| Problema | Causa | Solución |
|---|---|---|
| La primera conexión SSH falla con `Paramiko: 'No existing session'`. | RouterOS genera sus llaves SSH en la primera conexión y tarda en responder. | Volver a ejecutar la herramienta; las conexiones siguientes funcionan. |
| Ansible falla con `paramiko is not installed`. | El Ansible del sistema usa el Python del sistema, que no tenía Paramiko. | `sudo apt install python3-paramiko`. |
| Ansible falla con `The authenticity of host '192.168.100.2' can't be established`. | La llave SSH del router no está en `known_hosts`. | Conectarse una vez con `ssh admin@192.168.100.2` (o `ssh-keyscan`) y aceptar la llave. |
| Ansible falla con `Authentication failed: transport shut down or saw EOF`. | Si el usuario tiene llaves en `~/.ssh/id_*`, Paramiko las ofrece primero y RouterOS cierra la conexión antes de probar la contraseña. | Usar solo contraseña: `export ANSIBLE_PARAMIKO_LOOK_FOR_KEYS=False`. El script de pruebas ya define esta variable. |
| Al cambiar la identidad, también cambia el prompt de RouterOS (`[admin@MikroTik] >` pasa a `[admin@Hermes-Prueba] >`). | Netmiko espera por defecto el prompt detectado al conectarse. | `configurar_identidad.py` espera cualquier prompt de RouterOS al aplicar el cambio y verifica en una conexión nueva. |

Ansible también muestra advertencias de `ansible-pylibssh not installed` y de que el conector Paramiko está obsoleto. No impiden la ejecución, como ya se indicó en el README de Ansible.

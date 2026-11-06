# Automatización de MikroTik mediante Ansible

## 1. Introducción

Este módulo forma parte del proyecto Hermes Agent Ollama y tiene como objetivo automatizar la administración y configuración de dispositivos MikroTik mediante Ansible.

La solución permite establecer una conexión SSH entre el equipo de administración y un router MikroTik, consultar información del dispositivo, aplicar configuraciones y verificar que los cambios se hayan realizado correctamente.

Para desarrollar y probar esta implementación se utilizó Debian 13 como sistema de administración, GNS3 como entorno de simulación y MikroTik Cloud Hosted Router (CHR) como dispositivo de pruebas.

## 2. Objetivos

### Objetivo general

Implementar un sistema de automatización de redes mediante Ansible que permita administrar y validar configuraciones de un router MikroTik.

### Objetivos específicos

- Configurar un inventario de dispositivos administrados por Ansible.
- Establecer una conexión SSH con MikroTik.
- Consultar información general y recursos del router.
- Automatizar modificaciones de la configuración.
- Implementar validaciones para comprobar el estado del dispositivo.
- Aplicar condiciones para evitar modificaciones innecesarias.
- Documentar el proceso de instalación, configuración y ejecución.

## 3. Arquitectura de la solución

La implementación utiliza los siguientes componentes:

| Componente | Función |
|---|---|
| Debian 13 | Equipo de administración |
| Ansible Core 2.19.11 | Automatización de tareas |
| GNS3 3.0.6 | Simulación de la topología de red |
| QEMU 10.0.13 | Virtualización del router |
| MikroTik CHR 7.16 | Dispositivo administrado |
| SSH | Comunicación entre Debian y MikroTik |
| community.routeros | Colección para administrar RouterOS |

La comunicación se realiza desde Debian hacia el MikroTik utilizando SSH y el complemento `ansible.netcommon.network_cli`.

### Topología utilizada

- Equipo de administración: Debian.
- Dirección IP de administración del Debian: `192.168.100.1`.
- Dirección IP del MikroTik CHR: `192.168.100.2`.
- Puerto SSH: `22`.
- Interfaz del MikroTik utilizada: `ether1`.

La comunicación se realizó mediante una interfaz TAP conectada a la topología de GNS3.

## 4. Requisitos

Para reproducir el entorno se necesitan:

- Debian 13.
- Python 3.
- Ansible.
- GNS3.
- QEMU.
- Imagen de MikroTik CHR.
- Conectividad entre el equipo de administración y el router.
- Servicio SSH habilitado en MikroTik.
- Usuario con permisos suficientes para administrar RouterOS.

### Versiones utilizadas

| Herramienta | Versión |
|---|---|
| Debian | 13 |
| Ansible Core | 2.19.11 |
| GNS3 | 3.0.6 |
| QEMU | 10.0.13 |
| MikroTik CHR | RouterOS 7.16 |

## 5. Instalación y preparación del entorno

### 5.1. Instalar dependencias en Debian

Actualizar los repositorios:

```bash
sudo apt update
```

Instalar las dependencias principales:

```bash
sudo apt install -y \
python3 \
python3-pip \
pipx \
python3-pyqt6 \
python3-pyqt6.qtwebsockets \
python3-pyqt6.qtsvg \
qemu-system-x86 \
qemu-utils \
libvirt-clients \
libvirt-daemon-system \
virtinst \
ca-certificates \
curl \
gnupg2
```

Nota: la instalación inicial de `ubridge` mediante APT no fue posible en los repositorios utilizados. Se debe verificar su disponibilidad según el entorno de instalación de GNS3.

### 5.2. Verificar las herramientas

Comprobar Ansible:

```bash
ansible --version
```

Comprobar GNS3:

```bash
gns3 --version
gns3server --version
```

Comprobar QEMU:

```bash
qemu-system-x86_64 --version
```

### 5.3. Preparar el MikroTik CHR

Se utilizó una imagen de MikroTik CHR versión 7.16 en formato IMG.

Archivo utilizado:

```text
chr-7.16.img
```

La imagen se incorporó al entorno de virtualización de GNS3 para crear el router de pruebas.

## 6. Configuración de red

La comunicación entre Debian y MikroTik se realizó mediante una interfaz TAP.

Direcciones utilizadas:

| Dispositivo | Dirección IP |
|---|---|
| Debian | 192.168.100.1 |
| MikroTik CHR | 192.168.100.2 |

Comprobar las interfaces de red en Debian:

```bash
ip -br addr
```

Consultar las rutas:

```bash
ip route
```

Comprobar conectividad con el MikroTik:

```bash
ping -c 4 192.168.100.2
```

La prueba permitió confirmar conectividad entre ambos dispositivos.

## 7. Configuración SSH del MikroTik

El servicio SSH debe estar habilitado para permitir la administración remota.

Desde la consola de MikroTik:

```routeros
/ip service print
```

Si SSH está deshabilitado:

```routeros
/ip service enable ssh
```

Comprobar los usuarios:

```routeros
/user print detail
```

El usuario utilizado en las pruebas fue `admin`, perteneciente al grupo `full`.

Desde Debian se comprobó la conexión mediante:

```bash
ssh admin@192.168.100.2
```

La conexión permitió acceder a la terminal de RouterOS y ejecutar comandos de administración.

## 8. Estructura del módulo Ansible

La estructura implementada es:

```text
herramientas/
└── ansible/
    ├── inventory/
    │   ├── hosts.yml
    │   └── group_vars/
    │       └── mikrotik.yml
    └── playbooks/
        ├── router_status.yml
        ├── router_config.yml
        └── router_validation.yml
```

### Descripción de los archivos

| Archivo | Descripción |
|---|---|
| hosts.yml | Define los dispositivos administrados. |
| mikrotik.yml | Contiene las variables de conexión. |
| router_status.yml | Consulta el estado del dispositivo. |
| router_config.yml | Aplica modificaciones de configuración. |
| router_validation.yml | Comprueba y corrige configuraciones. |

## 9. Configuración del inventario

Archivo:

```text
inventory/hosts.yml
```

Contenido:

```yaml
---
all:
  children:
    mikrotik:
      hosts:
        router:
```

Este inventario define el grupo `mikrotik` y el dispositivo identificado como `router`.

### Variables de conexión

Archivo:

```text
inventory/group_vars/mikrotik.yml
```

Contenido:

```yaml
---
ansible_host: "{{ lookup('env', 'MT_HOST') }}"

ansible_connection: ansible.netcommon.network_cli
ansible_network_os: community.routeros.routeros

ansible_user: "{{ lookup('env', 'MT_USER') }}"
ansible_password: "{{ lookup('env', 'MT_PASS') }}"
ansible_port: "{{ lookup('env', 'MT_PORT') | default('22', true) }}"

ansible_connect_timeout: 15
ansible_command_timeout: 30
```

Estas variables permiten definir la dirección del router, el usuario, la contraseña, el puerto SSH y los parámetros de conexión.

## 10. Variables de entorno y seguridad

Las credenciales se almacenan en un archivo `.env` ubicado en la raíz del proyecto.

Ejemplo:

```env
MT_HOST=192.168.100.2
MT_USER=admin
MT_PASS=CONTRASEÑA_DEL_ROUTER
MT_PORT=22
```

El archivo `.env` no debe publicarse en GitHub.

Para preparar el archivo:

```bash
cp .env.example .env
```

Editar:

```bash
nano .env
```

Cargar las variables en la terminal:

```bash
set -a
source .env
set +a
```

Comprobar que las variables están disponibles sin mostrar la contraseña:

```bash
echo "$MT_HOST"
echo "$MT_USER"
test -n "$MT_PASS" && echo "Contraseña configurada"
echo "$MT_PORT"
```

**Importante:** nunca se deben incluir contraseñas reales en los archivos de inventario, playbooks, documentación o commits. Para entornos de producción se recomienda utilizar Ansible Vault o un gestor de secretos.

## 11. Colecciones de Ansible

La implementación utiliza las colecciones:

- `ansible.netcommon`
- `community.routeros`

Comprobar las colecciones instaladas:

```bash
ansible-galaxy collection list
```

La colección `community.routeros` proporciona los módulos necesarios para ejecutar comandos de administración sobre RouterOS.

## 12. Playbook de consulta del router

Archivo:

```text
playbooks/router_status.yml
```

Este playbook permite consultar:

- Identidad del router.
- Versión de RouterOS.
- Tiempo encendido.
- Memoria disponible.
- Uso de CPU.
- Espacio de almacenamiento.
- Arquitectura del dispositivo.

Para comprobar la sintaxis:

```bash
ansible-playbook \
-i herramientas/ansible/inventory/hosts.yml \
herramientas/ansible/playbooks/router_status.yml \
--syntax-check
```

Ejecutar:

```bash
ansible-playbook \
-i herramientas/ansible/inventory/hosts.yml \
herramientas/ansible/playbooks/router_status.yml
```

Durante las pruebas se obtuvo la siguiente información:

| Parámetro | Resultado |
|---|---|
| Identidad inicial | MikroTik |
| RouterOS | 7.16 Stable |
| CPU | QEMU |
| Memoria total | 384 MiB |
| Memoria libre | 140.5 MiB |
| Arquitectura | x86_64 |

## 13. Playbook de configuración

Archivo:

```text
playbooks/router_config.yml
```

Este playbook permite modificar parámetros específicos del router.

Las configuraciones aplicadas durante las pruebas fueron:

| Parámetro | Valor |
|---|---|
| Identidad | Hermes-CHR |
| Interfaz | ether1 |
| Comentario | Gestion Ansible - TAP |

Para validar la sintaxis:

```bash
ansible-playbook \
-i herramientas/ansible/inventory/hosts.yml \
herramientas/ansible/playbooks/router_config.yml \
--syntax-check
```

Ejecutar:

```bash
ansible-playbook \
-i herramientas/ansible/inventory/hosts.yml \
herramientas/ansible/playbooks/router_config.yml
```

La ejecución permitió modificar la identidad y el comentario de la interfaz.

Los resultados fueron verificados mediante consultas posteriores a RouterOS.

## 14. Playbook de validación e idempotencia

Archivo:

```text
playbooks/router_validation.yml
```

Este playbook comprueba que la configuración del MikroTik coincida con los valores definidos como deseados.

Las tareas principales son:

1. Consultar la identidad actual.
2. Consultar el comentario de la interfaz.
3. Comparar los valores actuales con los deseados.
4. Corregir la identidad cuando sea necesario.
5. Corregir el comentario cuando sea necesario.
6. Consultar nuevamente los valores.
7. Validar los resultados mediante aserciones.

La implementación utiliza condiciones `when` para evitar ejecutar modificaciones cuando los valores ya son correctos.

También utiliza `changed_when: false` en las consultas para evitar que se contabilicen como cambios.

### Ejecución

```bash
ansible-playbook \
-i herramientas/ansible/inventory/hosts.yml \
herramientas/ansible/playbooks/router_validation.yml
```

### Resultado esperado cuando la configuración ya es correcta

```text
PLAY RECAP
router : ok=6
         changed=0
         unreachable=0
         failed=0
         skipped=2
```

El resultado indica que las consultas y validaciones se ejecutaron correctamente y que las tareas de corrección no fueron necesarias.

### Prueba de idempotencia

Se ejecutó el mismo playbook dos veces consecutivas sin modificar la configuración del router.

En ambas ejecuciones se obtuvo:

```text
changed=0
failed=0
```

Esto demuestra que el playbook no realiza modificaciones innecesarias cuando el dispositivo ya presenta el estado deseado.

## 15. Pruebas realizadas

Durante el desarrollo se realizaron las siguientes pruebas:

| Prueba | Resultado |
|---|---|
| Verificación del inventario | Correcta |
| Conectividad IP con MikroTik | Correcta |
| Acceso SSH | Correcto |
| Consulta de identidad | Correcta |
| Consulta de recursos | Correcta |
| Configuración de identidad | Correcta |
| Configuración del comentario de ether1 | Correcta |
| Verificación de los valores configurados | Correcta |
| Validación de sintaxis de playbooks | Correcta |
| Primera ejecución de validación | Correcta |
| Segunda ejecución de validación | Correcta |
| Idempotencia en estado correcto | Comprobada |

La corrección automática ante una configuración alterada queda como prueba adicional de validación funcional.

## 16. Solución de problemas frecuentes

### 16.1. Error de autenticación SSH

Mensaje:

```text
Failed to authenticate: Authentication failed.
```

Posibles causas:

- Contraseña incorrecta en `.env`.
- Usuario incorrecto.
- Variables de entorno no cargadas.

Solución:

```bash
set -a
source .env
set +a
```

Comprobar las variables sin mostrar la contraseña.

### 16.2. Error de conexión SSH

Mensaje:

```text
Connection refused
```

Comprobar que el router esté encendido y que SSH esté habilitado:

```routeros
/ip service print
```

### 16.3. Error de sintaxis YAML

Ejecutar:

```bash
ansible-playbook \
-i herramientas/ansible/inventory/hosts.yml \
herramientas/ansible/playbooks/router_validation.yml \
--syntax-check
```

Revisar la indentación y las condiciones `when`.

### 16.4. Advertencias de Paramiko

Durante las pruebas se presentaron los siguientes mensajes:

```text
ansible-pylibssh not installed, falling back to paramiko
```

```text
The paramiko connection plugin is deprecated.
```

Estas advertencias indican que Ansible utiliza Paramiko como alternativa de conexión SSH debido a que `ansible-pylibssh` no está instalado.

En el entorno utilizado no impidieron la ejecución de los playbooks.

Se recomienda revisar la compatibilidad del transporte SSH con las futuras versiones de Ansible.

## 17. Procedimiento general de ejecución

Para utilizar el módulo desde la raíz del proyecto:

### Paso 1. Cargar las credenciales

```bash
set -a
source .env
set +a
```

### Paso 2. Comprobar el inventario

```bash
ansible-inventory \
-i herramientas/ansible/inventory/hosts.yml \
--graph
```

### Paso 3. Consultar el router

```bash
ansible-playbook \
-i herramientas/ansible/inventory/hosts.yml \
herramientas/ansible/playbooks/router_status.yml
```

### Paso 4. Aplicar configuración

```bash
ansible-playbook \
-i herramientas/ansible/inventory/hosts.yml \
herramientas/ansible/playbooks/router_config.yml
```

### Paso 5. Validar configuración

```bash
ansible-playbook \
-i herramientas/ansible/inventory/hosts.yml \
herramientas/ansible/playbooks/router_validation.yml
```

## 18. Conclusiones

La implementación permitió integrar Ansible con un router MikroTik CHR dentro de un entorno de simulación utilizando GNS3.

Se consiguió establecer comunicación SSH desde Debian, configurar un inventario de dispositivos y desarrollar playbooks para consultar, modificar y validar parámetros del router.

También se incorporaron condiciones para que las modificaciones solamente se ejecuten cuando los valores actuales sean diferentes de los valores deseados.

Las pruebas realizadas demostraron que Ansible puede administrar el dispositivo y comprobar su estado sin generar modificaciones innecesarias cuando la configuración ya es correcta.

Este módulo constituye una base para ampliar la automatización de redes dentro del proyecto Hermes Agent Ollama.

# Agente inteligente para la administración de redes MikroTik

## 1. Descripción del proyecto

El proyecto consiste en desarrollar un agente inteligente para facilitar la supervisión y administración de dispositivos MikroTik mediante inteligencia artificial.

El sistema permite interpretar solicitudes del usuario y utilizar herramientas desarrolladas en Python y Ansible para consultar información y realizar tareas de administración sobre los routers.

El objetivo es automatizar tareas de red, facilitar la gestión de los dispositivos y reducir la intervención manual, manteniendo controles de seguridad para las operaciones realizadas.

## 2. Tecnologías y herramientas utilizadas

| Tecnología | Descripción |
|---|---|
| Hermes Agent | Agente principal encargado de interpretar las solicitudes y coordinar las herramientas. |
| Ollama | Plataforma para ejecutar localmente el modelo de lenguaje. |
| Qwen 2.5 3B | Modelo de lenguaje utilizado por el agente. |
| Python | Lenguaje utilizado para desarrollar las herramientas de administración. |
| Netmiko | Biblioteca para establecer conexiones SSH con dispositivos de red. |
| Ansible | Herramienta para automatizar tareas mediante playbooks. |
| MikroTik RouterOS | Sistema operativo de los routers administrados. |
| WSL2 | Entorno Linux utilizado para el desarrollo en Windows. |
| Ubuntu 24.04 | Distribución Linux utilizada como entorno de trabajo. |
| Git y GitHub | Herramientas para el control de versiones y colaboración. |

## 3. Arquitectura del proyecto

El funcionamiento general se organiza de la siguiente manera:

1. El usuario realiza una solicitud.
2. Hermes Agent interpreta la solicitud.
3. Qwen 2.5 3B procesa el lenguaje mediante Ollama.
4. Hermes coordina la herramienta correspondiente.
5. Las herramientas Python o Ansible se comunican con el MikroTik.
6. Se obtiene y devuelve el resultado de la operación.

**Componentes principales:**

- Agente: Hermes Agent.
- Modelo de lenguaje: Qwen 2.5 3B.
- Ejecución local del modelo: Ollama.
- Herramientas de administración: Python, Netmiko y Ansible.
- Dispositivo administrado: MikroTik RouterOS.

## 4. Requisitos del sistema

Para ejecutar el proyecto se necesita:

- Windows 10 u 11.
- WSL2.
- Ubuntu 24.04.
- Python 3.
- Git.
- Una máquina virtual con MikroTik RouterOS.
- Acceso SSH al MikroTik.
- Ollama.
- Hermes Agent.
- Memoria RAM suficiente para ejecutar el modelo local.

Cada integrante puede utilizar su propia máquina virtual MikroTik, siempre que tenga conectividad desde Ubuntu y el servicio SSH habilitado.

## 5. Instalación del entorno de trabajo

### 5.1. Instalar WSL2 y Ubuntu

Desde PowerShell de Windows:

```powershell
wsl --install -d Ubuntu-24.04
```

Abrir Ubuntu una vez finalizada la instalación.

### 5.2. Actualizar Ubuntu

```bash
sudo apt update
sudo apt upgrade -y
```

Instalar las herramientas necesarias:

```bash
sudo apt install -y git python3 python3-pip python3-venv curl
```

### 5.3. Clonar el repositorio

```bash
git clone https://github.com/vane12-j/Hermes-Agent-Ollama_proyecto
```

Ingresar a la carpeta:

```bash
cd proyecto_redesProgramables
```

### 5.4. Crear el entorno virtual

```bash
python3 -m venv .venv
```

Activar el entorno:

```bash
source .venv/bin/activate
```

Actualizar pip:

```bash
python -m pip install --upgrade pip
```

### 5.5. Instalar las dependencias de Python

Ejecutar:

```bash
pip install -r requirements.txt
```

Las principales bibliotecas utilizadas son:

- `netmiko`: conexión SSH y comunicación con MikroTik.
- `ansible`: automatización de tareas mediante playbooks.

Si Ansible no está incluido en `requirements.txt`, instalarlo mediante:

```bash
pip install ansible
```

Comprobar las instalaciones:

```bash
python --version
pip show netmiko
ansible --version
```

## 6. Instalación de Ollama y Qwen

### 6.1. Instalar Ollama

Ejecutar en Ubuntu:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Comprobar la instalación:

```bash
ollama --version
```

### 6.2. Descargar el modelo Qwen 2.5 3B

```bash
ollama pull qwen2.5:3b
```

Probar el modelo:

```bash
ollama run qwen2.5:3b
```

Escribir un mensaje para comprobar que genera una respuesta.

### 6.3. Crear el modelo con contexto de 64K

Crear un archivo llamado `Modelfile`:

```bash
nano Modelfile
```

Agregar:

```text
FROM qwen2.5:3b
PARAMETER num_ctx 65536
```

Crear el modelo:

```bash
ollama create qwen2.5:3b-64k -f Modelfile
```

Comprobar los parámetros:

```bash
ollama show qwen2.5:3b-64k --parameters
```

Para comprobar el contexto efectivo del modelo en ejecución:

```bash
ollama ps
```

### 6.4. Configurar Ollama como proveedor de Hermes

Hermes debe configurarse para utilizar Ollama como proveedor personalizado, mediante su API compatible con OpenAI.

Endpoint:

```text
http://localhost:11434/v1
```

Modelo:

```text
qwen2.5:3b-64k
```

La configuración del proveedor y del modelo se realiza en el archivo:

```bash
nano ~/.hermes/config.yaml
```

### 6.5. Instalar Hermes Agent

Ejecutar:

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

Recargar la configuración de la terminal:

```bash
source ~/.bashrc
```

Comprobar la instalación:

```bash
hermes --version
```

### 6.6. Probar Hermes Agent

Ejecutar:

```bash
hermes -z "Responde solamente: HOLA"
```

La respuesta esperada es:

```text
HOLA
```

## 7. Configuración del MikroTik

Para realizar las pruebas se utiliza una máquina virtual con MikroTik RouterOS.

Cada integrante puede utilizar su propia máquina virtual.

### 7.1. Configurar el acceso SSH

Desde la terminal de MikroTik:

```routeros
/ip address print
```

Consultar los servicios:

```routeros
/ip service print
```

Habilitar SSH si está desactivado:

```routeros
/ip service enable ssh
```

### 7.2. Comprobar la conectividad

Desde Ubuntu ejecutar:

```bash
ping DIRECCION_IP_DEL_MIKROTIK
```

Probar la conexión SSH:

```bash
ssh USUARIO@DIRECCION_IP_DEL_MIKROTIK
```

El usuario debe tener permisos suficientes para las operaciones que realizará el proyecto.

## 8. Configuración de las variables de entorno

El proyecto incluye el archivo `.env.example`, que contiene una plantilla de las variables necesarias para conectarse al MikroTik.

### 8.1. Crear el archivo de configuración

Desde la raíz del proyecto:

```bash
cp .env.example .env
```

Editar:

```bash
nano .env
```

Configurar los siguientes valores:

```env
MT_HOST=192.168.56.7
MT_USER=admin
MT_PASS=TU_CONTRASEÑA
MT_PORT=22
```

Cada integrante debe utilizar la dirección IP, usuario y contraseña de su propia máquina virtual.

### 8.2. Cargar las variables

Ejecutar:

```bash
set -a
source .env
set +a
```

Comprobar que las variables necesarias estén configuradas sin mostrar la contraseña:

```bash
test -n "$MT_HOST" && echo "MT_HOST configurado"
test -n "$MT_USER" && echo "MT_USER configurado"
test -n "$MT_PASS" && echo "MT_PASS configurado"
echo "Puerto SSH: $MT_PORT"
```

**Importante:** el archivo `.env` contiene credenciales privadas. No debe subirse al repositorio.

## 9. Ejecución de las herramientas Python

Las herramientas iniciales de consulta se encuentran en:

```text
herramientas/python/
```

### 9.1. Consultar interfaces

Archivo:

```text
consultar_interfaces.py
```

Esta herramienta obtiene las interfaces configuradas en el MikroTik mediante el comando:

```routeros
/interface print
```

Ejecutar desde la raíz del proyecto:

```bash
python herramientas/python/consultar_interfaces.py
```

### 9.2. Consultar direcciones IP

Archivo:

```text
consultar_direcciones_ip.py
```

Esta herramienta obtiene las direcciones IP configuradas en el MikroTik mediante el comando:

```routeros
/ip address print
```

Ejecutar:

```bash
python herramientas/python/consultar_direcciones_ip.py
```

Ambas herramientas devuelven sus resultados en formato JSON e informan si la operación se realizó correctamente.

Estas operaciones son únicamente de consulta y no modifican la configuración del router.

### 9.3. Configurar la identidad del router

Archivo:

```text
configurar_identidad.py
```

Esta herramienta modifica la identidad (nombre) del MikroTik mediante el comando:

```routeros
/system identity set name=NOMBRE
```

Antes y después del cambio realiza los siguientes controles:

1. Valida el nombre solicitado: de 1 a 64 caracteres entre letras, números, `.`, `_` o `-`.
2. Consulta la identidad actual con `/system identity print`.
3. Si el router ya tiene la identidad solicitada, no realiza cambios.
4. Muestra el cambio y solicita confirmación al operador (`s` para confirmar).
5. Aplica el cambio.
6. Verifica, en una conexión nueva, que la identidad final coincida con la solicitada.

Ejecutar:

```bash
python herramientas/python/configurar_identidad.py --nombre Hermes-CHR
```

Ejemplo de confirmación:

```text
Cambio solicitado sobre el MikroTik:
  Identidad actual: MikroTik
  Identidad nueva:  Hermes-CHR
¿Confirma el cambio? [s/N]:
```

Si el operador ya aprobó el cambio por otro medio (por ejemplo, a través del agente), se puede omitir la pregunta con `--confirmar`:

```bash
python herramientas/python/configurar_identidad.py --nombre Hermes-CHR --confirmar
```

El resultado se devuelve en formato JSON:

| Campo | Descripción |
|---|---|
| `success` | Indica si la operación terminó correctamente. |
| `estado` | `aplicado`, `sin_cambios`, `cancelado` o `error`. |
| `identidad_anterior` | Identidad consultada antes del cambio. |
| `identidad_solicitada` | Identidad indicada con `--nombre`. |
| `identidad_final` | Identidad consultada después del cambio. |
| `cambio_aplicado` | Indica si se envió el cambio al router. |
| `verificado` | Indica si la identidad final coincide con la solicitada. |

Códigos de salida: `0` cambio aplicado o no necesario, `1` error, `2` cambio no confirmado por el operador.

## 10. Ejecución de Ansible

Para trabajar con las herramientas Ansible se requiere tener instalado Ansible y configurar el inventario con los datos de conexión del MikroTik.

Los playbooks del proyecto se organizan en:

```text
herramientas/ansible/
```

La ejecución de cada playbook se realiza desde la raíz del proyecto mediante:

```bash
ansible-playbook -i INVENTARIO PLAYBOOK.yml
```

El nombre del inventario y del playbook dependerá de los archivos disponibles en el proyecto.

Las operaciones de modificación deben realizar validaciones y verificaciones del estado del dispositivo.

## 11. Variables de entorno utilizadas

| Variable | Descripción | Ejemplo |
|---|---|---|
| `MT_HOST` | Dirección IP del MikroTik. | `192.168.56.7` |
| `MT_USER` | Usuario de conexión SSH. | `admin` |
| `MT_PASS` | Contraseña del usuario. | Valor privado |
| `MT_PORT` | Puerto SSH del router. | `22` |

## 12. Estructura del proyecto

```text
proyecto_redesProgramables/
│
├── herramientas/
│   ├── python/
│   │   ├── consultar_interfaces.py
│   │   ├── consultar_direcciones_ip.py
│   │   └── configurar_identidad.py
│   │
│   └── ansible/
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## 13. Consideraciones de seguridad

- No guardar contraseñas directamente en los scripts.
- No compartir archivos `.env`.
- Utilizar conexiones SSH para comunicarse con el MikroTik.
- Validar los parámetros antes de ejecutar operaciones.
- Verificar los resultados de las tareas realizadas.
- Solicitar confirmación antes de ejecutar cambios en la configuración del router.
- Limitar las herramientas a las funciones autorizadas.

## 14. Objetivo final

Integrar Hermes Agent, Qwen 2.5 3B, Ollama, Python y Ansible para desarrollar un agente inteligente capaz de interpretar solicitudes y realizar tareas de supervisión y administración controlada de routers MikroTik.

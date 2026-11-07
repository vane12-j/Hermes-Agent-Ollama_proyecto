# Resumen de pruebas de funcionamiento

- Fecha: 2026-11-06 19:15:27
- Router: 192.168.100.2:22 (usuario admin)
- Python: 3.13.5 | Ansible: ansible-playbook [core 2.19.11]
- Resultado: **16 de 16 casos correctos**

| # | Herramienta | Caso | Resultado | Detalle | Evidencia |
|---|---|---|---|---|---|
| 01 | consultar_interfaces | Lista las interfaces del router | PASA | success=true, aparece ether1 | [01_consultar_interfaces.txt](01_consultar_interfaces.txt) |
| 02 | consultar_direcciones_ip | Lista las direcciones IP del router | PASA | success=true, aparece 192.168.100.2 | [02_consultar_direcciones_ip.txt](02_consultar_direcciones_ip.txt) |
| 03 | configurar_identidad | Rechaza un nombre no válido sin conectarse | PASA | Nombre no válido: use de 1 a 64 caracteres entre letras, números, '.', '_' o '-'. | [03_identidad_nombre_invalido.txt](03_identidad_nombre_invalido.txt) |
| 04 | configurar_identidad | Consulta el estado actual y el operador rechaza el cambio | PASA | actual=MikroTik, estado=cancelado | [04_identidad_operador_rechaza.txt](04_identidad_operador_rechaza.txt) |
| 05 | configurar_identidad | Sin respuesta del operador (sin terminal) no se modifica | PASA | estado=cancelado | [05_identidad_sin_respuesta.txt](05_identidad_sin_respuesta.txt) |
| 06 | configurar_identidad | La identidad sigue siendo la original tras los rechazos | PASA | identidad=MikroTik, estado=sin_cambios | [06_identidad_sin_cambios_tras_rechazo.txt](06_identidad_sin_cambios_tras_rechazo.txt) |
| 07 | configurar_identidad | El operador confirma, se aplica y se verifica el cambio | PASA | MikroTik -> Hermes-Prueba, verificado=True | [07_identidad_operador_confirma.txt](07_identidad_operador_confirma.txt) |
| 08 | configurar_identidad | Repetir el mismo nombre no modifica ni pide confirmación | PASA | estado=sin_cambios, cambio_aplicado=False | [08_identidad_idempotencia.txt](08_identidad_idempotencia.txt) |
| 09 | configurar_identidad | Restaura la identidad original con --confirmar | PASA | identidad=MikroTik, estado=aplicado | [09_identidad_restaurar.txt](09_identidad_restaurar.txt) |
| 10 | ansible | Validación de sintaxis de router_status.yml | PASA | código de salida 0 | [10_ansible_sintaxis_router_status.txt](10_ansible_sintaxis_router_status.txt) |
| 11 | ansible | Validación de sintaxis de router_config.yml | PASA | código de salida 0 | [11_ansible_sintaxis_router_config.txt](11_ansible_sintaxis_router_config.txt) |
| 12 | ansible | Validación de sintaxis de router_validation.yml | PASA | código de salida 0 | [12_ansible_sintaxis_router_validation.txt](12_ansible_sintaxis_router_validation.txt) |
| 13 | ansible | Consulta de identidad y recursos (router_status.yml) | PASA | router : ok=4 changed=0 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0 | [13_ansible_router_status.txt](13_ansible_router_status.txt) |
| 14 | ansible | Primera ejecución de router_validation.yml | PASA | router : ok=8 changed=2 unreachable=0 failed=0 skipped=0 rescued=0 ignored=0 | [14_ansible_router_validation_1.txt](14_ansible_router_validation_1.txt) |
| 15 | ansible | Segunda ejecución de router_validation.yml (idempotencia) | PASA | router : ok=6 changed=0 unreachable=0 failed=0 skipped=2 rescued=0 ignored=0 | [15_ansible_router_validation_2.txt](15_ansible_router_validation_2.txt) |
| 16 | configurar_identidad | Restaura la identidad original tras las pruebas de Ansible | PASA | identidad=MikroTik, estado=aplicado | [16_identidad_restaurar.txt](16_identidad_restaurar.txt) |

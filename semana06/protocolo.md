# Protocolo de aplicación — versión 2

## 1. Identificación

| Campo | Valor |
|---|---|
| Equipo | Angelo Muñoz y Sebastián Cárcamo |
| Dominio del servicio | Sensores IoT |
| Versión del protocolo | 2.0 |
| Transporte | TCP, puerto 5000 |
| Codificación | UTF-8, un mensaje por línea, terminador `\n` |
| Modelo de concurrencia del servidor | hilo por cliente |
| Timeout de inactividad | 60 s (el servidor cierra la conexión) |

## 2. Formato general

- Petición `COMANDO [argumentos separados por espacio]\n`
- Respuesta correcta `OK [datos]\n`
- Respuesta de error `ERROR CODIGO [detalle]\n`
- El servidor responde exactamente UNA línea por cada línea recibida.
- Los comandos no distinguen mayúsculas; los argumentos de identificación sí.

## 3. Secuencia de una sesión

cliente                  servidor
|--- HOLA  ------------->|
|<-- OK HOLA  -----------|
|--- <operaciones...> ---------->|
|<-- OK ... / ERROR ... ---------|
|--- SALIR --------------------->|
|<-- OK CHAO --------------------|   (el servidor cierra)

**¿Es obligatorio HOLA antes de operar?** No. Si no se envía, el servidor acepta operaciones directamente.

## 4. Operaciones

| Comando | Argumentos | Respuesta OK | Errores posibles | ¿Modifica estado compartido? |
|---|---|---|---|---|
| HOLA | nombre | `OK HOLA nombre` | — | no |
| ACTUALIZAR | id_sensor valor | `OK id_sensor=valor` | `ERROR FORMATO ACTUALIZAR <id_sensor> <valor>`, `ERROR VALOR_INVALIDO` | sí |
| LEER | id_sensor | `OK id_sensor=valor` | `ERROR FORMATO LEER <id_sensor>`, `ERROR SENSOR_NO_ENCONTRADO` | no |
| REPORTE | — | `OK id1:val1 id2:val2 …` | — | no |
| ESPERA | segundos | `OK ESPERA seg` | `ERROR FORMATO ESPERA <segundos>` | no |
| SALIR | — | `OK CHAO` | — | no |

## 5. Códigos de error

| Código | Cuándo se produce |
|---|---|
| COMANDO_DESCONOCIDO | El comando recibido no existe en la tabla de operaciones. |
| FORMATO | Faltan argumentos requeridos o tienen un formato incorrecto. |
| VALOR_INVALIDO | El valor asignado al sensor no es una representación numérica válida (`float`). |
| SENSOR_NO_ENCONTRADO | Se intenta consultar un `id_sensor` que no ha sido registrado. |

## 6. Comportamiento ante situaciones anómalas

| Situación | Qué hace el servidor |
|---|---|
| Línea vacía | Responde `ERROR COMANDO_DESCONOCIDO`. |
| Cliente inactivo 60 s | Cierra la conexión TCP sin enviar mensaje. |
| Cliente se desconecta a mitad de una operación | Registra la desconexión abrupta en logs y sigue atendiendo al resto. |
| Dos clientes modifican el mismo dato a la vez | Las escrituras se serializan mediante un `Lock`; prevalece la última operación procesada. |
| Bytes no decodificables en UTF-8 | Se reemplazan por el carácter de sustitución UTF-8 (`errors='replace'`). |

## 7. Estado compartido

| Dato | Tipo | Valor inicial | Quién lo modifica |
|---|---|---|---|
| telemetria | dict sensor → valor | temp_salon: 21.5, presion_caldera: 101.3 | ACTUALIZAR |
| operaciones | int | 0 | Toda operación enviada por los clientes |

## 8. Historial de cambios

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0 | semana 4 | Servidor TCP secuencial. |
| 2.0 | semana 6 | Servidor concurrente (hilos), estado protegido con Lock, timeout de 60s y registro de errores. |
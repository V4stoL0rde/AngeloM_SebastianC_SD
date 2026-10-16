# Interfaz HTTP del servicio (anexo de protocolo.md)

## 9.1 Identificación

| Campo | Valor |
|---|---|
| Equipo | AngeloM_SebastianC_SD |
| Entrada única | `http://localhost:8080` (Nginx) |
| Formato | JSON, UTF-8 |
| Documentación interactiva | `http://localhost:8080/docs` |
| Réplicas de la API | api1, api2 |
| Dónde vive el estado | en el servidor TCP (`servidor.py`), la API no guarda nada |

## 9.2 Tabla de traducción, operación por operación

| Comando del protocolo de texto | Método y ruta HTTP | Cuerpo JSON | Respuesta correcta | Código |
|---|---|---|---|---|
| `REPORTE` | `GET /sensores` | (sin cuerpo) | `{"telemetria": {"presion": 101.3, "temp_salon": 21.5}, "replica": "api1"}` | 200 |
| `LEER <id_sensor>` | `GET /sensores/{id_sensor}` | (sin cuerpo) | `{"sensor": "temp_salon", "valor": 21.5, "replica": "api2"}` | 200 |
| `ACTUALIZAR <id_sensor> <valor>` | `POST /sensores/{id_sensor}/lecturas` | `{"valor": 24.5}` | `{"sensor": "temp_salon", "valor": 24.5, "replica": "api1"}` | 201 |

## 9.3 Tabla de errores

| Situación | Respuesta del protocolo de texto | Código HTTP | Quién responde |
|---|---|---|---|
| El sensor buscado no existe | `ERROR SENSOR_NO_ENCONTRADO` | 404 | la API |
| El valor enviado no es numérico | `ERROR VALOR_INVALIDO` | 400 | la API |
| Cuerpo o ruta con formato incorrecto | (no llega al servidor) | 422 | la API (Pydantic), antes de traducir |
| El servidor TCP no está disponible | (sin respuesta / conexión rechazada) | 503 | la API |
| El servidor TCP no responde a tiempo | (timeout) | 504 | la API |
| No queda ninguna réplica de la API viva | (sin respuesta) | 502 | Nginx |

## 9.4 Decisiones de diseño

- **¿Por qué esos sustantivos como recursos?**: Se eligió `/sensores` como colección principal de recursos y `/lecturas` como un subrecurso que representa los eventos de medición enviados en el tiempo, siguiendo el estándar REST.
- **¿Qué operación NO expusieron por HTTP y por qué?**: La operación `ESPERA` no se expuso públicamente vía HTTP para evitar ataques de denegación de servicio (DoS) bloqueando hilos del servidor con demoras artificiales.
- **¿Qué valida la API antes de traducir, y qué pasaría si no lo validara?**: Valida el tipo numérico del campo `valor` mediante Pydantic y el nombre del sensor con expresiones regulares. Si no lo validara, un cliente podría inyectar saltos de línea (`\n`) en el socket TCP rompiendo el protocolo de texto del servidor.
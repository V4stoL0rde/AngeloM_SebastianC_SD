# Observaciones — Semana 9, serialización explícita

**Equipo:** AngeloM_SebastianC  **Integrantes:** Angelo Muñoz y Sebastián Cárcamo  **Fecha:** 23-10-2026

## Paso 2 — Ida y vuelta de los codecs

Salida de `python codec.py`:

```
json  solicitud  89 bytes  b'{"operacion": "ACTUALIZAR", "argumentos": ["temperatura", "23.5"], "id": 7, "version": 2}'
json  respuesta  69 bytes  b'{"id": 7, "estado": "OK", "datos": ["temperatura=23.5"], "error": ""}'
bin   solicitud  37 bytes  b'\x02\x00\x00\x00\x07\x00\nACTUALIZAR\x02\x00\x0btemperatura\x00\x0423.5'
bin   respuesta  26 bytes  b'\x00\x00\x00\x07\x00\x01\x00\x10temperatura=23.5\x00\x00'
ida y vuelta OK en los dos codecs

```

Tamaño de la misma solicitud en JSON ____ bytes y en bin ____ bytes.

## Paso 3 — Medición

Salida de `python bench_codec.py 10000`:

```

| Mensaje   | Codec | Bytes promedio | Bytes totales | Codificar (ms) | Decodificar (ms) |
|-----------|-------|---------------:|--------------:|---------------:|-----------------:|
| Solicitud | json  |           74.7 |        746652 |           50.9 |             23.8 |
| Solicitud | bin   |           21.8 |        217762 |            9.7 |             11.8 |
| Respuesta | json  |          118.9 |       1189418 |           59.1 |             26.3 |
| Respuesta | bin   |           67.1 |        670528 |           17.9 |             24.0 |

Solicitud: el binario ocupa 71% menos bytes que JSON (JSON 75 B vs bin 22 B por mensaje)
Respuesta: el binario ocupa 44% menos bytes que JSON (JSON 119 B vs bin 67 B por mensaje)
```

Conclusión en dos líneas (cuánto ahorra el binario, cuál es más rápido, qué sacrificamos a cambio):

El formato binario es considerablemente más rápido y eficiente, ahorrando un 71% de espacio en solicitudes y un 44% en respuestas frente a JSON.
A cambio de este rendimiento superior y menor uso de red, se sacrifica la legibilidad humana directa de los mensajes.

## Paso 4 — Integración

| Prueba | codec=json | codec=bin |
|---|---|---|
| `HOLA` | | |
| `AGREGAR ...` (del dominio) | | |
| `LISTAR` | | |
| Error del dominio (por ejemplo stock insuficiente) | | |

## Paso 5 — Falla provocada

| Modo de `cliente_malo.py` | Qué vio el cliente | Qué dice el log del servidor | ¿El servidor siguió atendiendo? |
|---|---|---|---|
| `version` | modo=version codec=json respuesta Respuesta(id=1, estado='ERROR', datos=[], error='versión 1 no soportada, use 2') | sd_servidor   01:45:36 [cli-7] conectado ('172.18.0.3', 52276) sd_servidor   01:45:36 [cli-7] versión no soportada 1 desde ('172.18.0.3', 52276) | si, siguió atendiendo |
| `largo` | modo=largo codec=json ! sin respuesta en 5.0 s | sd_servidor   01:49:46 [cli-10] conectado ('172.18.0.3', 43410) sd_servidor   01:49:51 [cli-10] desconectado ('172.18.0.3', 43410) | si, siguió atendiendo |
| `basura` (codec json) | respuesta Respuesta(id=0, estado='ERROR', datos=[], error='mensaje mal formado (UnicodeDecodeError)') | sd_servidor   01:59:51 [cli-12] mensaje mal formado desde ('172.18.0.3', 39276) -> UnicodeDecodeError 'utf-8' codec can't decode byte 0x97 in position 0: invalid start byte | si, siguió atendiendo |
| `basura` (codec bin) | enviando 97af88ff42ed05e1586a1a5eccf84d5ba96d3a7b4d6903ca | sd_servidor   01:59:51 [cli-12] mensaje mal formado desde ('172.18.0.3', 39276) -> UnicodeDecodeError 'utf-8' codec can't decode byte 0x97 in position 0: invalid start byte | si, siguió atendiendo |
| `cruzado` | modo=cruzado codec=json
  codificando con bin respuesta Respuesta(id=0, estado='ERROR', datos=[], error='mensaje mal formado (JSONDecodeError)') | sd_servidor   02:02:47 [cli-14] mensaje mal formado desde ('172.18.0.3', 48714) -> JSONDecodeError Expecting value: line 1 column 1 (char 0) | si, siguió atendiendo |

¿Cuál de los dos codecs falló de forma más clara ante la basura y por qué?

El formato JSON falló de forma más clara ante datos basura, ya que al ser un formato de texto plano estructurado, cualquier corrupción o texto inesperado rompe inmediatamente el analizador sintáctico (parser), generando un error explícito de sintaxis.

## Para la semana autónoma

Una pregunta que nos quedó sobre serialización o protocolos:

_(escribir)_

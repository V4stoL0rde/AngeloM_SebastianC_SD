# Protocolo del servicio — versión 3 (Semana 9)

> Reemplaza a protocolo.md v2 de semana06/. Lo que cambia es la **sección 2**
> (ya no es una línea de texto, es un mensaje estructurado) y se agregan las
> secciones 7 y 8. El resto se copia de la v2 y se actualiza donde corresponda.

## 1. Identificación

| Campo | Valor |
|---|---|
| Equipo | Angelo Muñoz y Sebastián Cárcamo |
| Dominio |Sensores IoT |
| Versión del protocolo | 2 (campo `version` del mensaje) |
| Versión del documento | 3 |
| Transporte | TCP, puerto 5000 dentro de `sd_net` |

## 2. Formato del mensaje

Cada mensaje viaja **enmarcado**: 4 bytes con el largo (entero sin signo, big-endian) seguidos del cuerpo.

```
+------------+------------------------+
| largo (4B) | cuerpo (largo bytes)   |
+------------+------------------------+
```

El cuerpo se codifica con uno de dos **codecs**, elegido por la variable `CODEC`. Cliente y servidor deben usar el mismo.

### 2.1 Solicitud (cliente → servidor)

| Campo | Tipo | Descripción |
|---|---|---|
| `version` | entero | Versión del protocolo. El servidor rechaza las distintas de 2 |
| `id` | entero | Correlativo del cliente. La respuesta trae el mismo id |
| `operacion` | texto | Nombre de la operación en mayúsculas |
| `argumentos` | lista de textos | Argumentos de la operación, puede ser vacía |

### 2.2 Respuesta (servidor → cliente)

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | entero | Mismo id de la solicitud (0 si no se pudo leer la solicitud) |
| `estado` | `OK` o `ERROR` | Resultado |
| `datos` | lista de textos | Resultado cuando estado es OK |
| `error` | texto | Mensaje legible cuando estado es ERROR |

### 2.3 Codec `json`

Cuerpo en JSON UTF-8 con los campos anteriores como claves.

```json
{"operacion": "AGREGAR", "argumentos": ["tornillo", "25"], "id": 7, "version": 2}
```

### 2.4 Codec `bin`

Cuerpo binario con `struct`, big-endian. Los textos van con largo prefijado de 2 bytes y las listas con cantidad prefijada de 1 byte.

```
Solicitud: version(1B) id(4B) operacion(2B+texto) n_args(1B) [arg(2B+texto)]*
Respuesta: id(4B) estado(1B: 0=OK 1=ERROR) n_datos(1B) [dato(2B+texto)]* error(2B+texto)
```

## 3. Operaciones

_(Copien la tabla de la v2 y agreguen la columna de ejemplo de solicitud estructurada.)_

| Operación | Argumentos | Respuesta OK (`datos`) | Errores posibles |
|---|---|---|---|
| `HOLA` | — | saludo | — |
| `ECO` | texto libre | el mismo texto | — |
| `LISTAR` | — | un `clave=valor` por ítem | — |
| `AGREGAR` | producto, cantidad | `producto=stock_nuevo` | cantidad no entera, cantidad no positiva |
| `QUITAR` | producto, cantidad | `producto=stock_nuevo` | stock insuficiente |
| `ESPERA` | segundos | confirmación | — |
| `SALIR` | — | despedida, cierra conexión | — |
| _(las del equipo)_ | | | |
| `ACTUALIZAR` | id_sensor valor | `OK id_sensor=valor` | `ERROR FORMATO ACTUALIZAR <id_sensor> <valor>`, `ERROR VALOR_INVALIDO` | sí |
| `LEER` | id_sensor | `OK id_sensor=valor` | `ERROR FORMATO LEER <id_sensor>`, `ERROR SENSOR_NO_ENCONTRADO` | no |
| `REPORTE` | — | `OK id1:val1 id2:val2 …` | — | no |

## 4. Errores de protocolo

| Situación | Reacción del servidor |
|---|---|
| `version` distinta de 2 | Responde `ERROR` con el texto `versión X no soportada, use 2` y mantiene la conexión |
| Cuerpo que no se puede decodificar | Responde `ERROR mensaje mal formado (...)` con id 0 y **cierra esa conexión** |
| Largo anunciado mayor a 1 MB | Responde `ERROR` y cierra esa conexión |
| Largo anunciado mayor a lo enviado | Espera hasta `TIMEOUT_SERVIDOR` (30 s) y cierra esa conexión |
| Operación desconocida | Responde `ERROR operación desconocida` |

## 5. Concurrencia

_(Igual que la v2. Hilo por cliente, `Lock` sobre el estado compartido.)_

## 6. Ejemplo de sesión

```
> HOLA                      ->  OK Bienvenido al inventario v2
> AGREGAR tornillo 25       ->  OK tornillo=25
> QUITAR tornillo 30        ->  ERROR stock insuficiente de tornillo (25)
> LISTAR                    ->  OK tornillo=25
> SALIR                     ->  OK chao
```

## 7. Medición de codecs

| Mensaje   | Codec | Bytes promedio | Bytes totales | Codificar (ms) | Decodificar (ms) |
|-----------|-------|---------------:|--------------:|---------------:|-----------------:|
| Solicitud | json  |           74.7 |        746652 |           50.9 |             23.8 |
| Solicitud | bin   |           21.8 |        217762 |            9.7 |             11.8 |
| Respuesta | json  |          118.9 |       1189418 |           59.1 |             26.3 |
| Respuesta | bin   |           67.1 |        670528 |           17.9 |             24.0 |

Solicitud: el binario ocupa 71% menos bytes que JSON (JSON 75 B vs bin 22 B por mensaje)
Respuesta: el binario ocupa 44% menos bytes que JSON (JSON 119 B vs bin 67 B por mensaje)

Conclusión en dos líneas (cuánto ahorra el binario, cuál es más rápido, qué sacrificamos a cambio):

El formato binario es considerablemente más rápido y eficiente, ahorrando un 71% de espacio en solicitudes y un 44% en respuestas frente a JSON.
A cambio de este rendimiento superior y menor uso de red, se sacrifica la legibilidad humana directa de los mensajes.

## 8. Historial de cambios

| Versión doc | Fecha | Cambio |
|---|---|---|
| 1 | sem. 4 | Protocolo de texto por líneas |
| 2 | sem. 6 | Concurrencia, errores, operaciones del dominio |
| 3 | sem. 9 | Mensaje estructurado, enmarcado por largo, codecs json y bin, versión en el mensaje |

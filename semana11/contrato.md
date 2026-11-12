# Contrato del servicio · trabajo autónomo semana 11

Plazo jueves 12-11-2026 a las 18.00, en `semana11/` del repositorio del equipo.

## Qué hay que hacer
1. Agregar al menos **una operación nueva** a `proto/servicio.proto` con sus mensajes, sin cambiar los números de campo existentes.
2. Implementarla en `dominio.py` y exponerla en `servidor_grpc.py` y en `cliente_grpc.py`.
3. Regenerar los stubs y probarla desde el contenedor cliente.
4. Completar este archivo.

## Operaciones

| Operación | Qué hace | Modifica estado | Idempotente | Lleva `id_solicitud` | Errores posibles (código gRPC) |
|---|---|---|---|---|---|
| Listar | Devuelve todos los sensores y sus valores actuales | No | Sí | No | `UNIMPLEMENTED`, `UNAVAILABLE` |
| Actualizar | Crea o modifica el valor de un sensor | Sí | No | Sí | `INVALID_ARGUMENT`, `FAILED_PRECONDITION`, `DEADLINE_EXCEEDED` |
| Leer | Consulta el valor de un sensor específico | No | Sí | No | `INVALID_ARGUMENT`, `FAILED_PRECONDITION` |
| Eliminar | Borra un sensor existente del almacenamiento | Sí | No | Sí | `INVALID_ARGUMENT`, `FAILED_PRECONDITION`, `DEADLINE_EXCEEDED` |

## Mensajes y campos

| Mensaje | Campo | Número | Tipo | Significado |
|---|---|---|---|---|
| ListarSolicitud | *(ninguno)* | - | - | Solicitud vacía para listar |
| SensorItem | sensor | 1 | string | Nombre o identificador del sensor |
| SensorItem | valor | 2 | string | Valor actual registrado del sensor |
| ListarRespuesta | items | 1 | repeated SensorItem | Lista completa de sensores |
| ActualizarSolicitud | id_solicitud | 1 | string | Identificador único para at-most-once |
| ActualizarSolicitud | sensor | 2 | string | Nombre del sensor a actualizar |
| ActualizarSolicitud | valor | 3 | string | Nuevo valor a asignar |
| LeerSolicitud | sensor | 1 | string | Nombre del sensor a consultar |
| SensorRespuesta | sensor | 1 | string | Nombre del sensor afectado o consultado |
| SensorRespuesta | valor | 2 | string | Valor devuelto del sensor |
| EliminarSolicitud | id_solicitud | 1 | string | Identificador único para at-most-once |
| EliminarSolicitud | sensor | 2 | string | Nombre del sensor a eliminar |

## Decisiones
- ¿Por qué la operación nueva es o no es idempotente?La operación `Eliminar` no es idempotente porque altera y destruye el estado del servidor. La primera vez elimina el sensor de forma correcta, pero en una segunda ejecución con el mismo identificador fallará indicando que el sensor ya no existe (`FAILED_PRECONDITION`), a menos que se controle mediante el mecanismo de deduplicación con `id_solicitud` (`DEDUP=1`).
- ¿Qué pasaría si un cliente antiguo, que no conoce la operación nueva, sigue llamando al servidor? (pista, compatibilidad de Protocol Buffers) Gracias a la compatibilidad hacia adelante y hacia atrás de Protocol Buffers, el cliente antiguo puede seguir utilizando las operaciones tradicionales (`Listar`, `Actualizar`, `Leer`) sin problemas de serialización, ignorando la existencia del método `Eliminar`.
- Prueba realizada (comando y salida)
- *Comando:* `docker compose exec cliente python cliente_grpc.py eliminar temperatura`
- *Salida:* `[cliente]   OK sensor temperatura = 25.0`

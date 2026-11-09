# Observaciones semana 11 · Migración a gRPC

Equipo ……………… · Dominio ……………… · Fecha 06-11-2026

## 1. Contrato
- Archivo `proto/servicio.proto` con 3 operaciones.
- Operaciones que modifican estado y llevan `id_solicitud`: `ACTUALIZAR`
- Operaciones idempotentes (se pueden repetir sin efecto extra): `listar y leer`

## 2. Stubs generados
- Clase del stub en el cliente: `ControlSensoresStub` (nombre exacto en `servicio_pb2_grpc.py`)
- Clase base del servidor: `ControlSensoresServicer` 
- Qué hace el stub cuando llamamos `stub.Agregar(...)`, en dos líneas, con sus palabras: Empaqueta los datos en formato binario(bytes) estableciendo una conexion gRPC con el servidpr a traves de la red.
## 3. Equivalencia de errores JSON-RPC → gRPC

| Caso | JSON-RPC (semana 10) | gRPC (hoy) | Comando usado |
|---|---|---|---|
| Método inexistente | -32601 | UNIMPLEMENTED | `docker compose exec cliente python -c "import grpc; grpc.insecure_channel('servidor:50051').unary_unary('/sensores.v1.ControlSensores/Borrar')(b'', timeout=2)"` |
| Parámetros inválidos | -32602 | INVALID_ARGUMENT | `c python cliente_grpc.py actualizar "" ""` |
| Error del dominio | -32000 | FAILED_PRECONDITION | `c python cliente_grpc.py leer humedad` |
| Servidor caído | sin conexión | UNAVAILABLE | |
| Respuesta lenta | timeout del cliente | DEADLINE_EXCEEDED | |

Pistas. Parámetros inválidos con `agregar tornillo 0`. El cliente no deja llamar a un método inexistente, usen esta línea (cambien la ruta por la de su servicio).

```
docker compose exec cliente python -c "import grpc; grpc.insecure_channel('servidor:50051').unary_unary('/inventario.v1.Inventario/Borrar')(b'', timeout=2)"
```

El error muestra `status = StatusCode.UNIMPLEMENTED`.

## 4. Falla intermedia · semántica teórica frente a la observada

| # | Configuración | Qué vio el cliente | Stock final con `listar` | Semántica observada |
|---|---|---|---|---|
| 1 | `FALLA=no`, sin reintentos | | | |
| 2 | `FALLA=siempre`, sin reintentos | | | |
| 3 | `FALLA=siempre`, `--reintentos 2`, sin `DEDUP` | | | |
| 4 | `FALLA=siempre DEDUP=1`, `--reintentos 2` | | | |
| 5 | `docker compose kill servidor` durante una llamada | | | |

Pegar aquí las líneas relevantes de `docker compose logs servidor` de los casos 3 y 4.

```
```

## 5. Conclusión (cinco líneas como máximo)
¿Qué operaciones de su dominio serían peligrosas de reintentar sin `id_solicitud`? ¿Qué pasaría en la vida real?

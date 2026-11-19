# Observaciones, taller semana 12 (objetos distribuidos con Pyro5)

Equipo: AngeloM_SebastianC
Integrantes presentes: Angelo Muñoz, Sebastián Cárcamo
Fecha 13-11-2026

## Paso 1, nombres y servidor arriba

URI que entregó el servidor de nombres para `sd.<equipo>.inventario`
(pegar la salida de `python cliente_pyro.py uri`)
```
01:25:05 sd.AngeloM_SebastianC.sensores -> PYRO:sensores@servidor:9100
01:25:05 nombres registrados ['Pyro.NameServer', 'sd.AngeloM_SebastianC.sensores']
```

¿Qué partes de la URI reconocen? (protocolo, identificador del objeto, nodo, puerto)
- Protocolo: `PYRO`
- Identificador del objeto (`objectId`): `sensores`
- Nodo / Host: `servidor` (nombre del servicio/contenedor en la red Docker `sd_net`, en lugar de `localhost`, porque el cliente corre en otro contenedor)
- Puerto: `9100`
## Paso 2, su dominio como objeto remoto

Operaciones que expusieron y en qué clase quedó cada una

| Clase | Método | ¿Cambia estado? |
|---|---|---|
| `ControlSensores` | `listar()` | No (solo lectura de todos los sensores) |
| `ControlSensores` | `leer(sensor)` | No (solo consulta el valor de un sensor) |
| `ControlSensores` | `actualizar(sensor, valor)` | Sí (crea o sobrescribe el valor de un sensor) |
| `ControlSensores` | `eliminar(sensor)` | Sí (elimina un sensor del almacenamiento) |
| `ControlSensores` | `abrir_lote(cliente)` | No en el dominio; instancia y registra un objeto `LoteSensores` en el daemon |
| `ControlSensores` | `quien_soy()` | No en el dominio; incrementa el contador interno de llamadas de la instancia |
| `ControlSensores` | `lotes_vivos()` | No (consulta cuántos lotes siguen registrados en el daemon) |
| `LoteSensores` | `agregar(sensor, valor)` | Sí (modifica el estado interno del lote agregando lecturas pendientes) |
| `LoteSensores` | `ver()` | No (consulta el estado actual del lote) |
| `LoteSensores` | `confirmar()` | Sí (aplica todas las lecturas al dominio y desregistra el objeto del daemon) |
| `LoteSensores` | `cancelar()` | Sí (descarta el lote y desregistra el objeto del daemon sin tocar el dominio) |

## Paso 3, paso por referencia

Referencia que recibió el cliente al abrir el objeto con estado (`pedido` o el suyo)

```
01:58:34 recibí Proxy, referencia PYRO:obj_983853c0e6874a9faf89967676c5d30b@servidor:9100

```

¿Qué pasó con `POR_VALOR=1`? ¿Por qué el cliente rechaza el objeto?
Al configurar `POR_VALOR=1`, el servidor volvio a la instancia de `LoteSensores` sin guardarla en el daemon (`self._pyroDaemon.register`), por lo que Pyro5 intenta serializar el objeto completo para enviarlo por valor. El cliente lo rechaza lanzando `SerializeError` ya que por seguridad, el serializador de Pyro5 (`serpent`) bloquea la deserialización de clases personalizadas no registradas como tipos de datos en el cliente, y además un objeto con estado remoto perdería su vínculo con el servidor si se enviara como una copia local.


¿Qué pasó al usar la referencia después de confirmar?
El método `confirmar()` ejecuta `self._pyroDaemon.unregister(self)` para finalizar el ciclo de vida del objeto en el servidor. Al intentar llamar inmediatamente después a `lote.ver()`, el servidor responde con `CommunicationError` (`unknown object`), ya que la URI quedó convertida en una referencia colgante que apunta a un objeto que ya fue eliminado del daemon.



## Paso 4, modo de instancia
| Modo | Instancia del proxy A | Instancia del proxy B | ¿Comparten el contador? |
|---|---|---|---|
| single | Instancia 1 (llamadas 1 y 2) | Instancia 1 (llamadas 3 y 4) | Sí |
| session | Instancia 1 (llamadas 1 y 2) | Instancia 2 (llamadas 1 y 2) | No |

¿En cuál de los dos modos guardarían estado de un cliente? ¿Por qué el stock no cambia entre modos?
- El estado específico de una sesión de cliente se guardaría en modo `session` (donde cada conexión/proxy obtiene su propia instancia aislada), o bien en un objeto dedicado pasado por referencia como `LoteSensores`.
- El estado de los sensores (equivalente al stock) no cambia entre modos porque vive en variables a nivel de módulo (`_stock` y `_lock` dentro de `dominio.py`), las cuales son compartidas por todo el proceso Python del servidor sin importar cuántas instancias de `ControlSensores` cree el daemon.
## Paso 5, falla en tres tiempos

| Tiempo | Qué hicimos | Qué vio `vigilar` | Qué vio un cliente nuevo | Qué pasó con el estado |
|---|---|---|---|---|
| 1. servidor muerto | `docker compose kill servidor` | Reporta `FALLA de comunicación` (`CommunicationError`) cada segundo al fallar `listar()` y no poder reconectar. | Falla con `ERROR de comunicación` (`ConnectionRefusedError` / timeout) al intentar contactar a `servidor:9100`. | Se perdió por completo al morir el proceso en memoria RAM de `sd_servidor`. |
| 2. servidor vuelve | `docker compose start servidor` | Se reconecta automáticamente y vuelve a imprimir `ok, sensores {}`. | Consulta la URI en `nombres` y responde `sensores {}`. | El almacenamiento arrancó vacío (`{}`) y el lote abierto antes de la caída falló con `unknown object` (referencia colgante). |
| 3. nombres muerto y de vuelta | `kill nombres`, luego `start nombres` y finalmente `restart servidor` | **Siguió funcionando sin interrupciones** mientras `nombres` estuvo caído, porque ya tenía resuelta la URI directa. | Con `nombres` muerto falló con `NamingError`. Al revivir `nombres`, falló con `unknown name` por tabla vacía. Recién tras `restart servidor` volvió a funcionar. | El estado de los sensores en `servidor` no se vio afectado, pero `nombres` perdió su registro en memoria hasta que `servidor` se reinició. |

¿Qué nodo es punto único de falla en esta arquitectura? ¿Cómo lo resolverían?
Tanto `nombres` (punto único de falla para el descubrimiento inicial de servicios) como `servidor` (punto único de falla para el procesamiento y almacenamiento en memoria) actúan como punto unico de falla. Se resuelve persistiendo el estado de los sensores en base de datos/disco en lugar de memoria RAM, activando el re-registro periódico (`REREGISTRO > 0`) para recuperar el registro tras caídas del NameServer y desplegando réplicas del servidor.
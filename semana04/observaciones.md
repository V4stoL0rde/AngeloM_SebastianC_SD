# Observaciones — fallas provocadas · semana 4 · Equipo ______

Anoten lo que vieron, no lo que esperaban ver. Un tiempo sin unidad no sirve.

## Falla 1 — servidor muerto con el cliente conectado

Comando usado: `docker compose kill servidor`

| Pregunta | Respuesta |
|---|---|
| ¿Qué mensaje mostró el cliente? | CONEXIÓN PERDIDA: ConnectionError: el servidor cerró la conexión sin responder |
| ¿Cuánto tardó en aparecer desde que enviaron el comando? (ms o s) | 0.2 s|
| ¿El cliente supo que el servidor estaba muerto o solo que la conexión se cerró? |El cliente solo cree que el servidor se cerró.|
| Al levantar el servidor de nuevo, ¿se recuperó la sesión anterior (nombre, contador)? |Al levantar el servidor de nuevo no se recupero la sesion anterior.|

## Falla 2 — cliente sin red con el servidor vivo

Comando usado: `docker network disconnect sd_net cliente`

| Pregunta | Respuesta |
|---|---|
| ¿Qué mensaje mostró el cliente? |TIMEOUT: el servidor no respondió en 5 s. ¿Caído, sin red o lento? No se puede saber. |
| ¿Cuánto tardó en aparecer? | 5s|
| ¿Qué mostró el log del servidor en ese momento? |Se mantuvo igual no sufrio cambios. |
| Desde el punto de vista del cliente, ¿en qué se diferencia esta falla de la falla 1? |La diferecia es que en la primera falla el servidor se cerro la conexion sin responder y en la segunda falla no respondio pero no se sabe si se cayo,se quedo sin red o solo esta lento. |

## Segundo cliente mientras el primero está conectado (paso 3)

| Pregunta | Respuesta |
|---|---|
| ¿El segundo cliente logró conectarse (`connect`)? |No se logra conectar ya que hay un cliente conectado y solo se puede uno a la vez. |
| ¿Recibió respuesta a su primer comando? ¿Qué mostró? |  si, mostro el siguiente error TIMEOUT: el servidor no respondió en 5 s. ¿Caído, sin red o lento? No se puede saber. |
| ¿Qué mostró el log del servidor cuando el primer cliente hizo `SALIR`? |no muestra nada porque el cliente que esta en la cola queda conectado. |

## Conclusión del equipo (3 a 5 líneas)

¿Qué falacia de la semana 2 asumiría un programador que solo probara el camino feliz de este sistema? ¿Por qué el cliente no puede distinguir entre servidor caído, servidor ocupado y red cortada?
-La falacia de la semana 2 que asumaria un programador es la falacia 1 "la red es confiable" porque el cliente no puede distinguir entre servidor caido,servidor ocupado y red cortada porque confia en que todos los mensajes enviados llegaran y recibiran respuesta, el cliente no puede destinguir porque en la perspectiva a los ojos socket el sintoma es el mismo (arroja un TIMEOUT) despues de 5 segundos por el protocolo tsp que toma el silencio de la red y no sabe si esta lento o esta caido.
# Observaciones de la Semana 7

Equipo: AngeloM_SebastianC_SD
Integrantes: Angelo Muñoz y Sebastián Cárcamo
Dominio del servicio: Sensores IoT

## Paso 1  diagrama de despliegue v1 (el sistema de la semana 6)

Archivo entregado en `diagramas/despliegue_v1.png`
Cantidad de nodos, redes y puertos representados: 5 nodos (cliente, carga, servidor, otro_equipo, anfitrion) en la red sd_net con puerto TCP 5000 expuesto.

## Paso 2  revisión por pares

Equipo que revisó nuestro diagrama
Ítems de la pauta marcados como NO (copiar el número y el comentario)
Qué vamos a corregir primero y por qué

Equipo cuyo diagrama revisamos
Los dos hallazgos más importantes que les dejamos

## Paso 3  una operación como servicio REST

Operación del protocolo de texto elegida: `REPORTE`
Método y ruta HTTP: `GET /sensores`
Salida de la prueba contra api1:
`200   0.02 s  {"telemetria":{"presion":101.3,"temp_salon":21.5},"replica":"api1"}`

Salida de un caso de error y su código HTTP:
`404   0.01 s  {"detail":{"error":"SENSOR_NO_ENCONTRADO","detalle":"","replica":"api1"}}`

## Paso 4  dos réplicas detrás de Nginx

Salida de `cliente_http.py --repetir 4`:
`200   0.02 s  {"estado":"ok","replica":"api1"}`
`200   0.00 s  {"estado":"ok","replica":"api2"}`
`200   0.00 s  {"estado":"ok","replica":"api1"}`
`200   0.00 s  {"estado":"ok","replica":"api2"}`

¿Qué réplica atendió cada petición?: Se alternaron equitativamente entre `api1` y `api2` debido al algoritmo Round Robin configurado en `upstream` de Nginx.
¿El dato es el mismo sin importar la réplica? ¿Por qué?: Sí, porque las réplicas de la API son stateless (sin estado) y ambas se conectan mediante sockets TCP al mismo proceso central `sd_servidor` donde reside el estado en memoria.

## Paso 5  falla provocada en dos tiempos

### Tiempo 1, cae una réplica de la API
Predicción escrita ANTES de ejecutar: Al caer `api1`, Nginx detectará la falla al intentar conectarse y redirigirá las solicitudes transparentemente a `api2` sin interrumpir el servicio HTTP.
Comando usado: `docker compose kill api1`
Qué respondió el sistema:
`200   1.01 s  {"estado":"ok","replica":"api2"}`
`200   0.00 s  {"estado":"ok","replica":"api2"}`
`200   0.00 s  {"estado":"ok","replica":"api2"}`
`200   0.00 s  {"estado":"ok","replica":"api2"}`
¿Cuánto tardó la primera petición después de la caída?: Tardó 1.01 s debido al timeout de Nginx (`proxy_connect_timeout 1s`) antes de conmuta a la réplica viva.

### Tiempo 2, cae el servidor TCP
Predicción escrita ANTES de ejecutar: Las réplicas de la API no podrán establecer conexión TCP con el puerto 5000 y responderán con un código de error HTTP 503 (Service Unavailable).
Comando usado: `docker compose kill servidor`
Qué respondió el sistema y con qué código HTTP:
`503   4.01 s  {"detail":{"error":"SERVIDOR_NO_DISPONIBLE","detalle":"gaierror","replica":"api1"}}`
`503   3.86 s  {"detail":{"error":"SERVIDOR_NO_DISPONIBLE","detalle":"gaierror","replica":"api2"}}`
¿Qué se perdió al volver a levantar el servidor?: Se perdieron todas las lecturas y modificaciones realizadas durante la sesión anterior, volviendo al estado inicial definido en el código de `servidor.py`, debido a que el estado vive en la memoria RAM del proceso y no en una base de datos persistente.

### Conclusión en tres líneas
El nivel de API REST se pudo replicar sin problemas mediante Nginx por ser una capa de lógica stateless. En cambio, el servidor TCP de datos representa un punto único de falla (SPOF) al mantener el estado en la memoria RAM de un solo contenedor.
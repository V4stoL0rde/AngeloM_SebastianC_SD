# Observaciones — Semana 6

Equipo: AngeloM_SebastianC_SD
Integrantes: Angelo Muñoz y Sebastián Cárcamo
Dominio del servicio: Sensores IoT

## Paso 1 — servidor secuencial bajo carga

Comando ejecutado: `python cliente_carga.py --clientes 5 --comando "ESPERA 2"`
Tiempo por cliente:
  cliente   en fila   operacion      total   ultima respuesta
        4    2.06 s    2.00 s    4.06 s   OK ESPERA 2
        0    4.06 s    2.00 s    6.06 s   OK ESPERA 2
        1    6.06 s    2.00 s    8.06 s   OK ESPERA 2
        2    8.07 s    2.01 s   10.07 s   OK ESPERA 2
        3   10.07 s    2.00 s   12.08 s   OK ESPERA 2
TOTAL: 12.08 s
¿Qué esperaban? ¿Qué observaron?
Se esperaba que se demore unos 10s (2.00s por 5 clientes en cola), sin embargo se tardó alrededor de 12s

## Paso 2 — hilo por cliente bajo carga

Comando ejecutado: `docker compose exec carga python cliente_carga.py --clientes 5 --comando "ESPERA 2"`
  cliente   en fila   operacion      total   ultima respuesta
        1    0.02 s    2.00 s    2.02 s   OK ESPERA 2.0
        4    0.02 s    2.00 s    2.02 s   OK ESPERA 2.0
        0    0.02 s    2.00 s    2.02 s   OK ESPERA 2.0
        3    0.02 s    2.00 s    2.02 s   OK ESPERA 2.0
        2    0.02 s    2.00 s    2.02 s   OK ESPERA 2.0
TOTAL: 2.02 s
Diferencia respecto al Paso 1 y explicación:
La principal diferencia es que no usa una cola como en el servidor secuencial, ya que puede atender a los 5 clientes en simultáneo.

## Paso 3 — condición de carrera

Operación que modifica estado compartido usada: ``ACTUALIZAR temp_salon 25.0` y el contador global `operaciones`.`
Valor esperado: `1000` (50 clientes x 20 repeticiones).
Valor observado SIN Lock: operaciones_totales=1000
Valor observado CON Lock: operaciones_totales=1000
¿Dónde exactamente está la sección crítica en su código?
En `servidor.py`, dentro de la función `procesar()` al modificar `estado["operaciones"]` y en `op_actualizar()` al modificar el diccionario `estado["telemetria"]`. Ambas secciones están delimitadas por el bloque `with seccion_critica():`.

## Paso 4 — despliegue con docker compose

Salida de `docker compose ps`:
NAME          IMAGE              COMMAND                SERVICE    CREATED              STATUS              PORTS
sd_carga      semana6-carga      "sleep infinity"       carga      3 minutes ago        Up 3 minutes        
sd_cliente    semana6-cliente    "sleep infinity"       cliente    3 minutes ago        Up 3 minutes        
sd_servidor   semana6-servidor   "python servidor.py"   servidor   About a minute ago   Up About a minute   0.0.0.0:5000->5000/tcp, [::]:5000->5000/tcp

IP del host publicada para la prueba cruzada: 172.23.144.1

## Paso 5 — prueba cruzada

Equipo cuyo servidor probamos:
¿Su protocolo.md alcanzó para conectarse sin preguntar? (sí / no, qué faltó)
Mensajes enviados y respuestas obtenidas:
Qué falló y por qué:

Equipo que probó nuestro servidor:
Qué reportaron:

## Falla provocada — desconexión abrupta

Comando usado para provocarla:
Qué registró el log del servidor:
sd_servidor  | 2026-10-08 22:56:07,248 [servidor] cli-47228 conexion de ('172.18.0.4', 47228)
sd_servidor  | 2026-10-08 22:56:07,248 [servidor] cli-47240 conexion de ('172.18.0.4', 47240)
sd_servidor  | 2026-10-08 22:56:07,249 [servidor] cli-47256 conexion de ('172.18.0.4', 47256)
sd_servidor  | 2026-10-08 22:56:17,247 [servidor] cli-47228 cierre de ('172.18.0.4', 47228) | operaciones_totales=3
sd_servidor  | 2026-10-08 22:56:17,248 [servidor] cli-47240 cierre de ('172.18.0.4', 47240) | operaciones_totales=3
sd_servidor  | 2026-10-08 22:56:17,248 [servidor] cli-47256 cierre de ('172.18.0.4', 47256) | operaciones_totales=3
¿El servidor siguió atendiendo a los demás? Evidencia:

No siguió atendiendo a los demás...evidencia:
PS C:\Users\angel\OneDrive\Documentos\GitHub\AngeloM_SebastianC_SD\semana6> docker compose exec carga python cliente_carga.py --clientes 3 --comando "REPORTE"  
service "carga" is not running
# Mediciones — Laboratorio N°1 (Semana 2)

**Equipo:** __AngeloM_SebastianC_SD_____________   **Integrantes:** ___Angelo MUñoz___ / _Sebastian Carcamo______________
**Fecha:** 28-08-2026   **Entorno:** Docker Desktop (Windows) / otro: ________

## Paso 1 — Línea base
| Métrica | Valor |
|---|---|
| RTT ping (promedio) | _0.073__ ms |
| Throughput iperf3 |  29.3___ Gbit/s |

## Pasos 2 y 3 — Latencia inyectada (100 llamadas)
| Latencia `tc` | Total (s) | Promedio (ms) | Máx (ms) | ¿Esperado? (sí/no, por qué) |
|---|---|---|---|---|
| 0 ms (base)  |0.011 | 0.1 |0.4 | Si, por que representa un pequeño tiempo de procesamiento natural del sistema y su red base|
| 50 ms |5.043 |50.4 |5.07 |Sí. El promedio (50.4 ms) es exactamente la latencia inyectada (50 ms) más el overhead natural (~0.4 ms). El tiempo total (~5s) es lógico porque 100 llamadas x 50 ms = 5000 ms osea 5 segundos. |
| 200 ms |20.052 |200.5 |201.1 |Sí reflejan los 200 ms inyectados más el overhead (~0.5 ms). El tiempo total (~20s) es esperado porque 100 llamadas x 200 ms = 20000 ms es decir 20 segundos.|
| 500 ms |50.056 |500.6 |501.0 |Sí coincide con la latencia inyectada. El tiempo total de ~50 segundos es la consecuencia directa de realizar 100 llamadas secuenciales con 500 ms de retraso cada una (100 x 500 = 50000 ms).|

## Paso 4 — Pérdida de paquetes
| Pérdida `tc` | Throughput iperf3 | Total cliente (s) | Observación |
|---|---|---|---|
| 1% | 13.4 Gbits/s|0.423 |Cayo drasticamente el ancho de banda. El throughput bajo a 29.3 Gbit/s, una perdida de solo 1% obliga a reducir su ventana de congestion y retransmitir paquetes cortando su rendimiento a menos de la mitad|
| 5% | 384 Mbits/s|1.054 |Colapso de rendimiento, el throughput cae de forma abrupta a 384 Mbits/s, las retransmisiones contantes impiden que la conexion gane velocidad y el tiempo de respuesta del cliente sube notablemente. |
| 20% | 1.21 Mbits/s|5.231 | Red practicamente inservible, ya que el throughput es minimo y el tiempo del cliente supera los 5 segundos con una perdida tan alta como esta la conexion sufre timeouts contantes y TCP apenas logfra enviar datos |
| 100% (falla provocada) | — | | ¿Qué hizo el cliente? El error que marco fue:[cliente] error de red: [Errno 113] No route to host ¿Y con TIMEOUT_S=3? Lanzo este mensaje [cliente] TIMEOUT tras 3.0s esperando al servidor (0 llamadas completadas)  |

## Falacia que asumimos sin advertirlo
Asumimoa la Falcia 1: La red es confiale

En clinetes.py.la variable TIMEOUT se inicializa como None por desperfecto, asumiendo que la red nunca perdera paquetes ni dejara de responder. Al ocurrir un fallo total como la perdida del 100%, el programa no tiene un tiempo limite para abortar y se queda bloqueado en la llamada f.readline() esperando una respuesta que jamas llega. La solucion es definir siempre un timepo de espera explicion y gestionar la excepcion de desconexion en la aplicacion._____________________________________________________

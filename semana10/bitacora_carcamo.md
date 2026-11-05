# Bitácora individual — Semana 10

**Nombre:** Sebastián Cárcamo  **Equipo:** AngeloM_SebastianC
**Archivo:** `semana10/bitacora_carcamo.md` en el repositorio del equipo. **Entrega:** jueves 5 de noviembre de 2026, 18.00.

Esta bitácora es individual. Cada integrante escribe la suya con sus propias horas y sus propias palabras. No lleva nota, pero es un formativo obligatorio del programa y se revisa.

## Registro de sesiones

Una fila por sesión de trabajo. Las horas deben sumar al menos 8 entre los cuatro bloques.

| Fecha | Horas | Bloque | Qué estudié o hice | Qué me costó | Qué pregunté o respondí en el foro |
|---|---|---|---|---|---|
| 29/10/2026 | 2.0 | 1 Lecturas | Lectura de Tanenbaum (cap. 4.2) y Coulouris (cap. 5) sobre el funcionamiento de RPC, proxies, esqueletos y paso de parámetros. | Diferenciar la semántica de paso de parámetros por valor vs. por referencia en entornos distribuidos. | Consulté sobre la semántica de fallo (at-most-once vs at-least-once) descrita en Tanenbaum. |
| 01/11/2026 | 2.0 | 2 RMI, CORBA, DCOM | Investigación de tecnologías de objetos distribuidos heredadas para completar las columnas de RMI, CORBA y DCOM en el cuadro comparativo. | Entender la complejidad del protocolo IIOP de CORBA y cómo el ORB traduce tipos entre distintos lenguajes. | Discutí en el foro por qué DCOM presenta problemas al atravesar cortafuegos y routers con NAT. |
| 04/11/2026 | 2.0 | 3 JSON-RPC 2.0 | Lectura de la especificación JSON-RPC 2.0, resolución de los ejercicios prácticos a mano y redacción de la conclusión del cuadro. | Separar correctamente los errores del protocolo de los errores de dominio (-32000 a -32099). | Respondí una duda sobre el comportamiento del servidor ante notificaciones (ausencia del campo id). |
| 04/11/2026 | 2.0 | 3 JSON-RPC 2.0 | Lectura de la especificación JSON-RPC 2.0, resolución de los ejercicios prácticos a mano y redacción de la conclusión del cuadro. | Separar correctamente los errores dl protocolo de los errores de dominio (-32000 a -32099). | Respondí una duda sobre el comportamiento del servidor ante notificaciones (ausencia del campo id). |
| 05/11/2026 | 2.0 | 4 Prototipo | Implementación de las operaciones del dominio en `rpc.py`, ejecución del servidor FastAPI y validación con los comandos `curl`. | Capturar adecuadamente las excepciones de dominio en Python para evitar que FastAPI retorne un HTTP 500 no estructurado. | Aporté un tip en el foro sobre la flag `-i` en `curl` para visualizar el código HTTP 204 en notificaciones. |

## Tres preguntas de cierre (responder con sus palabras, 3 a 5 líneas cada una)

1. **¿Qué tienen en común JSON-RPC 2.0 y el protocolo v3 que escribieron en la semana 9? ¿Qué decisión tomó la especificación por ustedes?**
Ambos esquemas comparten la necesidad de mantener un id de correlación para asociar peticiones con respuestas, manejo de versiones explícito y un desacople entre los errores del dominio y la capa física. JSON-RPC 2.0 tomó por nosotros la decisión del formato de serialización en JSON, los nombres de las claves de la estructura (`method`, `params`, `jsonrpc`, `error`) y el estándar de códigos numéricos de error.

2. **¿Por qué RMI, CORBA y DCOM casi no se usan en sistemas nuevos y qué los reemplazó?**
Se dejaron de utilizar por estar fuertemente acoplados a plataformas específicas (Java en RMI, Windows en DCOM), depender de protocolos binarios difíciles de depurar y no ser amigables con firewalls o NAT. Fueron reemplazados principalmente por soluciones basadas en HTTP y JSON (como APIs REST o JSON-RPC) y por gRPC para comunicaciones de alto rendimiento en microservicios.

3. **¿Qué parte del prototipo les costó más y cómo la resolvieron?**
La parte más compleja fue implementar el despachador en `atender()` para que acepte tanto listas como diccionarios en `params` de forma dinámica (`*params` o `**params`) sin romper el flujo. Se resolvió estructurando bloques de control `try-except` especificando `TypeError` y `ValueError` para retornar los códigos de error `-32602` y `-32000` respectivamente.

## Autoevaluación

| Afirmación | Sí | Parcial | No |
|---|---|---|---|
| Leí las secciones asignadas y puedo explicar la diferencia entre RPC y objetos distribuidos | X | | |
| Aporté al cuadro comparativo con fuentes propias |  |X | |
| Puedo explicar el código del endpoint `/rpc` línea por línea | |X | |
| Probé los seis casos de error del prototipo con `curl` | X | | |
| Participé en el foro al menos una vez |  | | X|
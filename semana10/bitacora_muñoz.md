# Bitácora individual — Semana 10

**Nombre:** Angelo Muñoz  **Equipo:** AngeloM_SebastianC[cite: 12]
**Archivo:** `semana10/bitacora_muñoz.md` en el repositorio del equipo. **Entrega:** jueves 5 de noviembre de 2026, 18.00[cite: 12].

Esta bitácora es individual. Cada integrante escribe la suya con sus propias horas y sus propias palabras. No lleva nota, pero es un formativo obligatorio del programa y se revisa[cite: 12].

## Registro de sesiones

Una fila por sesión de trabajo. Las horas deben sumar al menos 8 entre los cuatro bloques.

| Fecha | Horas | Bloque | Qué estudié o hice | Qué me costó | Qué pregunté o respondí en el foro |
|---|---|---|---|---|---|
| 31/10/2026 | 2.0 | 1 Lecturas | Lectura de Tanenbaum (cap. 4.2) y Coulouris (cap. 5) sobre el funcionamiento de RPC, stubs y paso de parámetros. | Comprender la diferencia exacta entre paso de parámetros por valor y por referencia en entornos distribuidos. | Revisé conceptos de stubs y su similitud con el marshalling de la semana 9. |
| 02/11/2026 | 2.0 | 2 RMI, CORBA, DCOM | Investigación de tecnologías heredadas para completar las columnas del cuadro comparativo (orígenes, modelos y protocolos). | Sintetizar los detalles técnicos de los protocolos de transporte específicos de cada arquitectura (como JRMP e IIOP). | Consulté sobre las limitaciones de DCOM cruzando cortafuegos corporativos. |
| 04/11/2026 | 2.0 | 3 JSON-RPC 2.0 | Lectura de la especificación JSON-RPC 2.0 y resolución de ejercicios prácticos sobre peticiones, respuestas y códigos de error. | Mapear correctamente los rangos de errores del servidor y del dominio con los códigos estándar (-32000 a -32700). | Compartí dudas sobre el manejo de notificaciones sin ID de correlación. |
| 04/11/2026 | 2.0 | 4 Prototipo | Adaptación del script `rpc.py` con las operaciones IoT del dominio y ejecución de los casos de prueba con `curl`. | Resolver el conflicto inicial de sintaxis en PowerShell al ejecutar `curl` sin especificar `curl.exe`. | Verifiqué el comportamiento del código HTTP 204 ante peticiones de tipo notificación. |

## Tres preguntas de cierre (responder con sus palabras, 3 a 5 líneas cada una)

1. **¿Qué tienen en común JSON-RPC 2.0 y el protocolo v3 que escribieron en la semana 9? ¿Qué decisión tomó la especificación por ustedes?**
Ambos comparten la necesidad estructural de un identificador de correlación (`id`) para vincular solicitudes con respuestas, control de versiones y un manejo de errores robusto desacoplado de la capa física de transporte. La especificación JSON-RPC 2.0 tomó por nosotros la decisión exacta de la sintaxis basada en JSON, los nombres de los atributos (`method`, `params`, `result`) y los códigos estandarizados de error.

2. **¿Por qué RMI, CORBA y DCOM casi no se usan en sistemas nuevos y qué los reemplazó?**
Estas tecnologías sufren de un fuerte acoplamiento a plataformas específicas (como Java o Windows con DCOM), utilizaban protocolos binarios complejos que fallaban drásticamente al atravesar firewalls y requiriendo entornos de ejecución pesados. Fueron reemplazadas por enfoques modernos basados en HTTP, JSON (como REST o JSON-RPC) y gRPC debido a su simplicidad e interoperabilidad universal.

3. **¿Qué parte del prototipo les costó más y cómo la resolvieron?**
Lo que más costó fue configurar correctamente el despachador (`atender`) en FastAPI para que admitiera de forma flexible parámetros enviados tanto en formato de lista como de objeto (`**params`). Se resolvió analizando detalladamente el esqueleto provisto por la guía, estructurando bloques `try-except` adecuados para capturar errores de tipo y valor, y realizando pruebas unitarias iterativas.

## Autoevaluación

| Afirmación | Sí | Parcial | No |
|---|---|---|---|
| Leí las secciones asignadas y puedo explicar la diferencia entre RPC y objetos distribuidos | X | | |
| Aporté al cuadro comparativo con fuentes propias | X | | |
| Puedo explicar el código del endpoint `/rpc` línea por línea | | X | |
| Probé los seis casos de error del prototipo con `curl` | X | | |
| Participé en el foro al menos una vez | | | X |
# Cuadro comparativo — RMI, CORBA, DCOM y JSON-RPC

**Equipo:** AngeloM_SebastianC  **Integrantes:** Angelo Muñoz, Sebastian C.  **Semana 10, trabajo autónomo**

Completen cada celda con una o dos frases propias (no copiar y pegar). Donde una tecnología no aplique, escriban "no aplica" y por qué.

| Criterio | Java RMI | CORBA | DCOM | JSON-RPC 2.0 |
|---|---|---|---|---|
| **Año y origen (quién lo creó y para qué)** | Creado por Sun Microsystems en 1997 para invocar métodos de objetos Java de forma distribuida. | Desarrollado a principios de los 90 por el consorcio OMG para lograr interoperabilidad multilenguaje. | Creado por Microsoft en 1996 para extender el modelo de componentes COM a redes distribuidas. | Especificación ligera formalizada en 2010 por el JSON-RPC Working Group para llamadas remotas simples. |
| **Modelo (objetos remotos o procedimientos remotos)** | Basado en objetos remotos con identidad y estado gestionados por referencias. | Objetos distribuidos independientes del lenguaje gestionados mediante un ORB. | Componentes y objetos distribuidos acoplados estrechamente al modelo de Windows. | Procedimientos o métodos remotos sin estado acoplados a estructuras de texto JSON. |
| **Contrato o IDL (cómo se declara la interfaz)** | Interfaces de programación escritas en código nativo Java. | Archivo IDL (Interface Definition Language) independiente del lenguaje de programación. | MIDL (Microsoft Interface Definition Language) y bibliotecas de tipos compiladas. | No requiere un IDL formal; se documenta mediante la especificación de métodos y parámetros de la API. |
| **Transporte y formato de los mensajes** | JRMP (Java Remote Method Protocol) en formato binario. | IIOP (Internet Inter-ORB Protocol) sobre TCP/IP en formato binario. | ORPC (sobre DCE/RPC), empleando un formato binario propietario de Microsoft. | Agnóstico al transporte (HTTP, WebSockets), utilizando un formato de texto claro basado en JSON. |
| **Lenguajes y plataformas que soporta** | Estrictamente exclusivo para el ecosistema Java. | Multilenguaje gracias a la traducción de los ORB. | Principalmente orientado al ecosistema Windows y lenguajes compatibles con COM. | Compatible con cualquier lenguaje de programación capaz de serializar y deserializar JSON. |
| **Referencias remotas y estado (¿el servidor recuerda al cliente?)** | Sí, el cliente maneja referencias remotas con recolección de basura distribuida. | Sí, soporta referencias a objetos remotos (IOR) y mantenimiento de estado en el servidor. | Sí, administra conteo de referencias remotas a través del sistema operativo. | No almacena referencias remotas; el modelo operativo es completamente sin estado (*stateless*). |
| **Manejo de errores (cómo viaja un fallo al cliente)** | Mediante excepciones estándar del lenguaje (`RemoteException`). | Excepciones de sistema estandarizadas definidas por CORBA. | Códigos de retorno binarios `HRESULT` y excepciones nativas de COM. | Objeto estructurado con códigos de error estándar (`code`), mensaje descriptivo y datos opcionales. |
| **Relación con las cinco decisiones de la semana 9 (enmarcado, versión, id, errores, tipos)** | Resuelve tipos y errores mediante serialización; enmarcado y versión atados al protocolo JRMP. | Estandariza tipos, errores y enmarcado a nivel de la especificación del protocolo IIOP. | Resuelve tipos y errores mediante la infraestructura nativa de componentes Windows. | Resuelve enmarcado (vía transporte), versión explícita (`"2.0"`), ID de correlación y separación de errores. |
| **Estado actual (vigente, legado, reemplazado por qué)** | Legado / Obsoleto en la práctica actual, reemplazado por REST y gRPC. | Legado, relegado a sistemas corporativos heredados muy específicos. | Obsoleto, reemplazado en la industria por tecnologías web modernas y gRPC. | Vigente y ampliamente utilizado en microservicios, APIs ligeras y Web3. |
| **Caso de uso típico, real o histórico** | Sistemas empresariales cerrados desarrollados íntegramente sobre Java. | Integración de sistemas corporativos heterogéneos a gran escala en banca o telecomunicaciones. | Aplicaciones de escritorio distribuidas en redes de área local corporativas basadas en Windows. | APIs asíncronas, microservicios internos y pasarelas de intercambio descentralizado. |

## Conclusión del equipo (5 a 8 líneas)

De las cuatro tecnologías evaluadas, **JSON-RPC 2.0** es la que guarda mayor similitud con el protocolo binario v3 que construimos en la semana 9, ya que ambos comparten la necesidad de un identificador de correlación (*id*), control de versiones y un manejo estricto de códigos de error desacoplados de la capa de transporte. Para implementar un servicio interno en la actualidad, elegiríamos **gRPC** debido a su alto rendimiento y tipado estricto, mientras que para una API pública optaríamos por **JSON-RPC 2.0** o **REST** por su universalidad y facilidad de depuración mediante HTTP.

## Fuentes consultadas

Mínimo tres, con formato autor, título, año y enlace.

1. Tanenbaum, A. y Van Steen, M. (2017). *Sistemas distribuidos, principios y paradigmas*. Capítulo 4.
2. Coulouris, G. et al. (2001). *Sistemas Distribuidos. Conceptos y diseño*. Capítulo 5.
3. JSON-RPC Working Group (2010). *JSON-RPC 2.0 Specification*. Recuperado de jsonrpc.org/specification.
# Protocolo de aplicación — Equipo ______

Versión 0.1 · semana 4 · Este archivo evoluciona cada semana junto con el servicio.

## 1. Transporte

- Protocolo de transporte: TCP
- Puerto del servidor: 5000
- Codificación: UTF-8
- Delimitador de mensaje: una línea terminada en `\n`
- Quién inicia: el cliente. El servidor solo responde.

## 2. Mensajes

Completen la tabla. Una fila por comando. La operación propia del equipo va al final.

| Comando (cliente → servidor) | Argumentos | Respuesta (servidor → cliente) | ¿Cambia el estado de la conexión? |
|---|---|---|---|
| `HOLA <nombre>` | nombre, texto libre | `OK hola <nombre>` | Sí, guarda el nombre |
| `ECO <texto>` | texto libre | `ECO <texto>` | No lo guarda |
| `CONTAR` | ninguno | `OK <numero>` | no |
| `SALIR` | ninguno | `ADIOS` | Si, finaliza la conexión |
| (cualquier otro) | ninguno | `ERROR comando desconocido` | no |
| `LIMA` (operación propia) | ninguno | `LIMÓN` | no |

## 3. Estado

- ¿Qué recuerda el servidor de cada conexión? __Depende de si es una desconexión del cliente o un cierre del servidor, si es la primera, recuerda el contador del comando `CONTAR`, pero si es la segunda, no recuerda nada. ____
- ¿Qué pasa con ese estado cuando el cliente se desconecta? ___El estado de `CONTAR` es recordado por el servidor___
- Si el servidor se reinicia mientras un cliente está conectado, ¿qué pierde el cliente? ___Todo, incluido el estado que se guarda___

## 4. Secuencia típica

Dibujen o describan una sesión completa, desde `connect` hasta `ADIOS`.

```
cliente                servidor
   |---- connect --------->|
   |---- HOLA seba ------->|
   |<--- OK hola seba -----|
   |---- CONTAR ---------->|
   |<--- OK 1 -------------|
   |---- LIMA ------------>|
   |<--- LIMÓN ------------|
   |---- CONTAR ---------->|
   |<--- OK 2 -------------|
   |---- SALIR ----------->|
   |<--- ADIOS ------------|
   |         (cierre)      |
```

## 5. Errores

| Situación | Qué ve el cliente | Qué ve el servidor |
|---|---|---|
| Comando desconocido | `ERROR comando desconocido` | log con el comando |
| Servidor caído durante la sesión | CONEXIÓN PERDIDA: ConnectionError: el servidor cerró la conexión sin responder | servidor exited with code 137 |
| Cliente sin red durante la sesión | TIMEOUT: el servidor no respondió en 5 s. ¿Caído, sin red o lento? No se puede saber | Nada |
| Cliente corta sin `SALIR` (Ctrl+C) | corte abrupto desde el cliente (sin SALIR) | cierre de 172.18.0.3:42188 (1 mensajes) |

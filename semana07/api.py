"""Puerta HTTP (API REST) delante del servidor TCP de Sensores IoT.

Cada petición HTTP se TRADUCE a una línea del protocolo de texto, se envía
al servidor TCP y la respuesta se traduce de vuelta a JSON y a un código HTTP.

    GET  /salud                        -> Verificación de salud
    GET  /sensores                     -> REPORTE
    GET  /sensores/{id_sensor}         -> LEER <id_sensor>
    POST /sensores/{id_sensor}/lecturas -> ACTUALIZAR <id_sensor> <valor>
"""
import os
import socket

from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, Field

SERVIDOR_HOST = os.environ.get("SERVIDOR_HOST", "servidor")
SERVIDOR_PUERTO = int(os.environ.get("SERVIDOR_PUERTO", "5000"))
TIMEOUT_SERVIDOR = float(os.environ.get("TIMEOUT_SERVIDOR", "3"))
REPLICA = os.environ.get("REPLICA", socket.gethostname())

app = FastAPI(
    title="API de Sensores IoT",
    version="1.0",
    description="Puerta HTTP del servicio de Sensores IoT. Semana 7."
)

ID_SENSOR = Path(pattern=r"^[a-zA-Z0-9_]{1,30}$", description="identificador del sensor")

# Código de error del protocolo de texto -> código de estado HTTP
ERRORES = {
    "SENSOR_NO_ENCONTRADO": 404,
    "VALOR_INVALIDO": 400,
    "FORMATO": 400,
    "COMANDO_DESCONOCIDO": 501,
}


class Lectura(BaseModel):
    valor: float = Field(description="valor numérico de la telemetría")


# ----------------------------------------------------------------- Hablar con el nivel de datos
def pedir(linea: str) -> str:
    """Envía UNA línea al nivel de datos y devuelve UNA línea de respuesta."""
    try:
        with socket.create_connection((SERVIDOR_HOST, SERVIDOR_PUERTO),
                                      timeout=TIMEOUT_SERVIDOR) as s:
            s.sendall((linea + "\n").encode("utf-8"))
            respuesta = s.makefile("r", encoding="utf-8").readline().strip()
    except socket.timeout:
        raise HTTPException(504, {"error": "SERVIDOR_NO_RESPONDE", "replica": REPLICA})
    except OSError as e:
        raise HTTPException(503, {"error": "SERVIDOR_NO_DISPONIBLE",
                                  "detalle": e.__class__.__name__, "replica": REPLICA})
    if not respuesta:
        raise HTTPException(503, {"error": "SERVIDOR_CERRO_LA_CONEXION", "replica": REPLICA})
    return respuesta


def traducir(respuesta: str) -> list[str]:
    """'OK a b c' -> ['a','b','c']. 'ERROR CODIGO detalle' -> excepción HTTP."""
    partes = respuesta.split()
    if partes[0] == "OK":
        return partes[1:]
    codigo = partes[1] if len(partes) > 1 else "DESCONOCIDO"
    raise HTTPException(ERRORES.get(codigo, 500),
                        {"error": codigo, "detalle": " ".join(partes[2:]), "replica": REPLICA})


# ----------------------------------------------------------------- Recursos REST
@app.get("/salud")
def salud():
    return {"estado": "ok", "replica": REPLICA}


@app.get("/sensores")
def obtener_reporte():
    partes = traducir(pedir("REPORTE"))
    datos = {p.split(":")[0]: float(p.split(":")[1]) for p in partes if ":" in p}
    return {"telemetria": datos, "replica": REPLICA}


@app.get("/sensores/{id_sensor}")
def leer_sensor(id_sensor: str = ID_SENSOR):
    partes = traducir(pedir(f"LEER {id_sensor}"))
    clave_val = partes[0]
    nombre, val = clave_val.split("=")
    return {"sensor": nombre, "valor": float(val), "replica": REPLICA}


@app.post("/sensores/{id_sensor}/lecturas", status_code=201)
def actualizar_sensor(lectura: Lectura, id_sensor: str = ID_SENSOR):
    partes = traducir(pedir(f"ACTUALIZAR {id_sensor} {lectura.valor}"))
    clave_val = partes[0]
    nombre, val = clave_val.split("=")
    return {"sensor": nombre, "valor": float(val), "replica": REPLICA}
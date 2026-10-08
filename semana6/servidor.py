"""Servidor TCP concurrente (hilo por cliente) — Dominio: Sensores IoT."""
import logging
import os
import socket
import threading
import time

HOST = os.environ.get("HOST", "0.0.0.0")
PUERTO = int(os.environ.get("PUERTO", "5000"))
SIN_LOCK = os.environ.get("SIN_LOCK", "0") == "1"
TIMEOUT_CLIENTE = int(os.environ.get("TIMEOUT_CLIENTE", "60"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [servidor] %(threadName)s %(message)s"
)

# ----------------------------------------------------------------- Estado compartido
estado = {
    "telemetria": {
        "temp_salon": 21.5,
        "presion": 101.3
    },
    "operaciones": 0
}
lock = threading.Lock()


class SinLock:
    """Sustituto de Lock cuando se evalúan condiciones de carrera (SIN_LOCK=1)."""
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def seccion_critica():
    return SinLock() if SIN_LOCK else lock


# ----------------------------------------------------------------- Operaciones IoT
def op_actualizar(arg):
    partes = arg.split(maxsplit=1)
    if len(partes) < 2:
        return "ERROR FORMATO ACTUALIZAR <id_sensor> <valor>"
    id_sensor = partes[0]
    try:
        valor = float(partes[1])
    except ValueError:
        return "ERROR VALOR_INVALIDO"

    with seccion_critica():
        time.sleep(0.001)  # Ventana para evidenciar la condición de carrera si SIN_LOCK=1
        estado["telemetria"][id_sensor] = valor

    return f"OK {id_sensor}={valor}"


def op_leer(arg):
    id_sensor = arg.strip()
    if not id_sensor:
        return "ERROR FORMATO LEER <id_sensor>"
    
    with seccion_critica():
        if id_sensor in estado["telemetria"]:
            return f"OK {id_sensor}={estado['telemetria'][id_sensor]}"
    return "ERROR SENSOR_NO_ENCONTRADO"


def op_reporte(arg):
    with seccion_critica():
        items = " ".join(f"{k}:{v}" for k, v in sorted(estado["telemetria"].items()))
    return f"OK {items}"


def op_espera(arg):
    try:
        seg = float(arg)
    except ValueError:
        return "ERROR FORMATO ESPERA <segundos>"
    time.sleep(seg)  # Operación lenta fuera de la sección crítica
    return f"OK ESPERA {seg}"


OPERACIONES = {
    "ACTUALIZAR": op_actualizar,
    "LEER": op_leer,
    "REPORTE": op_reporte,
    "ESPERA": op_espera,
}


def procesar(linea):
    """Procesa cada comando enviado y devuelve (respuesta, seguir)."""
    partes = linea.strip().split(" ", 1)
    cmd = partes[0].upper() if partes and partes[0] else ""
    arg = partes[1] if len(partes) > 1 else ""

    if cmd == "HOLA":
        return f"OK HOLA {arg or 'anonimo'}", True
    if cmd == "SALIR":
        return "OK CHAO", False

    if cmd in OPERACIONES:
        with seccion_critica():
            estado["operaciones"] += 1
        return OPERACIONES[cmd](arg), True

    return "ERROR COMANDO_DESCONOCIDO", True


# ----------------------------------------------------------------- Atención al cliente
def atender(conn, addr):
    logging.info("conexion de %s", addr)
    conn.settimeout(TIMEOUT_CLIENTE)
    try:
        with conn, conn.makefile("r", encoding="utf-8", errors="replace") as entrada:
            for linea in entrada:
                respuesta, seguir = procesar(linea)
                conn.sendall((respuesta + "\n").encode("utf-8"))
                if not seguir:
                    break
    except (ConnectionResetError, BrokenPipeError) as e:
        logging.warning("cliente %s se desconecto abruptamente (%s)", addr, e.__class__.__name__)
    except socket.timeout:
        logging.warning("cliente %s inactivo %ss, cerrando", addr, TIMEOUT_CLIENTE)
    except Exception as e:
        logging.error("error inesperado con %s: %r", addr, e)
    finally:
        logging.info("cierre de %s | operaciones_totales=%s", addr, estado["operaciones"])


def main():
    logging.info("Iniciando servidor IoT (SIN_LOCK=%s, TIMEOUT=%ss)...", SIN_LOCK, TIMEOUT_CLIENTE)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PUERTO))
        srv.listen(64)
        logging.info("escuchando en %s:%s", HOST, PUERTO)
        while True:
            conn, addr = srv.accept()
            threading.Thread(
                target=atender,
                args=(conn, addr),
                name=f"cli-{addr[1]}",
                daemon=True
            ).start()


if __name__ == "__main__":
    main()
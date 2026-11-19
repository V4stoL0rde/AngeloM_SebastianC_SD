"""
Cliente Pyro5 del servicio de Sensores IoT, semana 12.

Uso (dentro del contenedor cliente, o con Python local)
  python cliente_pyro.py uri
  python cliente_pyro.py listar
  python cliente_pyro.py actualizar temperatura 23.5
  python cliente_pyro.py leer temperatura
  python cliente_pyro.py eliminar temperatura
  python cliente_pyro.py quien --veces 2
  python cliente_pyro.py lote temperatura:24.0 humedad:65 [--esperar 20]
  python cliente_pyro.py vivos
  python cliente_pyro.py vigilar [--cada 1]

Variables
  NOMBRES_HOST (nombres)  NOMBRES_PUERTO (9090)  EQUIPO (AngeloM_SebastianC)
"""
import argparse
import os
import sys
import time

from Pyro5.api import Proxy, locate_ns, register_dict_to_class
from Pyro5.errors import (CommunicationError, DaemonError, NamingError,
                          SerializeError, get_pyro_traceback)

NS_HOST = os.environ.get("NOMBRES_HOST", "nombres")
NS_PUERTO = int(os.environ.get("NOMBRES_PUERTO", "9090"))
EQUIPO = os.environ.get("EQUIPO", "AngeloM_SebastianC")
NOMBRE = f"sd.{EQUIPO}.sensores"


# Las excepciones también viajan serializadas (por valor). Pyro5 solo sabe
# reconstruir las de Python. Las propias del dominio hay que enseñárselas.
import dominio  # noqa: E402


def _a_excepcion(nombre_clase, datos):
    clase = getattr(dominio, nombre_clase.split(".")[-1])
    return clase(*datos.get("args", ()))


for _nombre in ("ErrorDominio", "ErrorParametros"):
    register_dict_to_class(f"dominio.{_nombre}", _a_excepcion)


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def sensores():
    """Proxy a ControlSensores. La URI se resuelve en el servidor de nombres."""
    proxy = Proxy(f"PYRONAME:{NOMBRE}@{NS_HOST}:{NS_PUERTO}")
    proxy._pyroTimeout = 5
    return proxy


def cmd_uri(_):
    with locate_ns(host=NS_HOST, port=NS_PUERTO) as ns:
        log(f"{NOMBRE} -> {ns.lookup(NOMBRE)}")
        log(f"nombres registrados {sorted(ns.list().keys())}")


def cmd_listar(_):
    with sensores() as srv:
        log(f"sensores {srv.listar()}")


def cmd_actualizar(a):
    with sensores() as srv:
        log(f"actualizar -> {srv.actualizar(a.sensor, a.valor)}")


def cmd_leer(a):
    with sensores() as srv:
        log(f"leer -> {srv.leer(a.sensor)}")


def cmd_eliminar(a):
    with sensores() as srv:
        log(f"eliminar -> {srv.eliminar(a.sensor)}")


def cmd_quien(a):
    """Mismo proxy varias veces y después un proxy nuevo. Muestra el modo."""
    for etiqueta in ("proxy A", "proxy B"):
        with sensores() as srv:
            for _ in range(a.veces):
                log(f"{etiqueta} -> {srv.quien_soy()}")


def cmd_vivos(_):
    with sensores() as srv:
        log(f"lotes vivos en el servidor {srv.lotes_vivos()}")


def reintentar_confirmar(uri, segundos):
    """Vuelve a llamar confirmar() sobre la misma URI hasta que el servidor
    conteste. Si contesta 'unknown object', no tiene sentido seguir."""
    limite = time.time() + segundos
    while True:
        try:
            with Proxy(uri) as lote:
                return lote.confirmar()
        except CommunicationError as e:
            if "unknown object" in str(e) or time.time() > limite:
                raise
            time.sleep(1)


def cmd_lote(a):
    lecturas = []
    for item in a.lecturas:
        sensor, sep, valor = item.partition(":")
        if not sep or not sensor or not valor:
            log(f"ERROR de uso. Las lecturas van como sensor:valor, recibí {item}")
            sys.exit(1)
        lecturas.append((sensor, valor))

    with sensores() as srv:
        lote = srv.abrir_lote(os.environ.get("HOSTNAME", "cliente"))
        lote._pyroTimeout = 5
        log(f"recibí {type(lote).__name__}, referencia {lote._pyroUri}")
        for sensor, valor in lecturas:
            lote.agregar(sensor, valor)
        log(f"estado en el servidor {lote.ver()}")
        if a.esperar:
            log(f"espero {a.esperar} s antes de confirmar (momento para la falla)")
            time.sleep(a.esperar)
        try:
            resultado = lote.confirmar()
        except CommunicationError as e:
            log(f"se cortó la conexión ({type(e).__name__}). Reintento con la "
                "MISMA referencia durante 30 s, levanten el servidor")
            resultado = reintentar_confirmar(lote._pyroUri, 30)
        log(f"confirmar -> {resultado}")
        log("uso la referencia después de confirmar")
        lote.ver()


def cmd_vigilar(a):
    """Llama listar() cada a.cada segundos con el MISMO proxy y reporta fallas."""
    srv = sensores()
    while True:
        try:
            log(f"ok, sensores {srv.listar()}  [{srv._pyroUri}]")
        except CommunicationError as e:
            log(f"FALLA de comunicación {type(e).__name__} {e}")
            try:
                srv._pyroReconnect(tries=1)
                log("reconectado")
            except (CommunicationError, NamingError) as e2:
                log(f"no pude reconectar {type(e2).__name__}")
        except NamingError as e:
            log(f"FALLA de nombres {e}")
        time.sleep(a.cada)


def main():
    p = argparse.ArgumentParser(description="Cliente Pyro5, semana 12")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("uri").set_defaults(f=cmd_uri)
    sub.add_parser("listar").set_defaults(f=cmd_listar)

    s = sub.add_parser("actualizar")
    s.add_argument("sensor")
    s.add_argument("valor")
    s.set_defaults(f=cmd_actualizar)

    for nombre, f in (("leer", cmd_leer), ("eliminar", cmd_eliminar)):
        s = sub.add_parser(nombre)
        s.add_argument("sensor")
        s.set_defaults(f=f)

    sub.add_parser("vivos").set_defaults(f=cmd_vivos)

    s = sub.add_parser("quien")
    s.add_argument("--veces", type=int, default=2)
    s.set_defaults(f=cmd_quien)

    s = sub.add_parser("lote")
    s.add_argument("lecturas", nargs="+", help="sensor:valor")
    s.add_argument("--esperar", type=int, default=0)
    s.set_defaults(f=cmd_lote)

    s = sub.add_parser("vigilar")
    s.add_argument("--cada", type=float, default=1)
    s.set_defaults(f=cmd_vigilar)

    a = p.parse_args()
    try:
        a.f(a)
    except KeyboardInterrupt:
        pass
    except NamingError as e:
        log(f"ERROR de nombres. No encuentro {NOMBRE}. {e}")
        sys.exit(2)
    except DaemonError as e:
        log(f"ERROR del daemon. La referencia apunta a un objeto que ya no existe. {e}")
        sys.exit(3)
    except SerializeError as e:
        log(f"ERROR de serialización. El servidor intentó enviar un objeto por valor. {e}")
        sys.exit(4)
    except CommunicationError as e:
        if "unknown object" in str(e):
            log("ERROR. El servidor responde, pero el objeto de esa referencia "
                f"ya no existe (referencia colgante). {e}")
            sys.exit(3)
        log(f"ERROR de comunicación. {type(e).__name__} {e}")
        sys.exit(5)
    except Exception as e:  # error del dominio que viene desde el servidor
        log(f"ERROR remoto {type(e).__name__} {e}")
        if os.environ.get("TRAZA") == "1":
            print("".join(get_pyro_traceback()))
        sys.exit(6)


if __name__ == "__main__":
    main()
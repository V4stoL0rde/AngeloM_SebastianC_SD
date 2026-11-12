"""
Dominio del servicio, sin nada de red. Semana 11.

Este archivo es lo que NO cambia cuando cambia el transporte. Lo usan
rpc.py (JSON-RPC, semana 10) y servidor_grpc.py (gRPC, semana 11).
"""
import threading

_lock = threading.Lock()
_stock = {}



class ErrorDominio(Exception):
    """Regla del negocio que no se cumple, por ejemplo sensor no encontrado."""


class ErrorParametros(Exception):
    """Parámetros con valor inválido."""


def _validar(sensor, valor):
    if not sensor:
        raise ErrorParametros("el sensor no puede estar vacío")
    if not valor:
        raise ErrorParametros("el valor no puede estar vacío")


def listar():
    with _lock:
        return dict(_stock)


def actualizar(sensor, valor):
    _validar(sensor, valor)
    with _lock:
        _stock[sensor] = valor
        return {"sensor": sensor, "valor": valor}


def leer(sensor):
    if not sensor:
        raise ErrorParametros("el sensor no puede estar vacío")
    with _lock:
        if sensor not in _stock:
            raise ErrorDominio(f"sensor {sensor} no encontrado")
        return {"sensor": sensor, "valor": _stock[sensor]}


def eliminar(sensor):
    if not sensor:
        raise ErrorParametros("el sensor no puede estar vacío")
    with _lock:
        if sensor not in _stock:
            raise ErrorDominio(f"sensor {sensor} no encontrado")
        valor = _stock.pop(sensor)
        return {"sensor": sensor, "valor": valor}

"""
Dominio del servicio, sin nada de red. Semana 11.

Este archivo es lo que NO cambia cuando cambia el transporte. Lo usan
rpc.py (JSON-RPC, semana 10) y servidor_grpc.py (gRPC, semana 11).
El equipo reemplaza el inventario de referencia por las operaciones de su
dominio, las mismas que ya tenía en semana10/rpc.py.
"""
import threading

_lock = threading.Lock()
_stock = {}


class ErrorDominio(Exception):
    """Regla del negocio que no se cumple, por ejemplo stock insuficiente."""


class ErrorParametros(Exception):
    """Parámetros con valor inválido."""


def _validar(producto, cantidad):
    if not producto:
        raise ErrorParametros("producto vacío")
    if cantidad <= 0:
        raise ErrorParametros("cantidad debe ser mayor que cero")


def listar():
    with _lock:
        return dict(_stock)


def agregar(producto, cantidad):
    _validar(producto, cantidad)
    with _lock:
        _stock[producto] = _stock.get(producto, 0) + cantidad
        return {"producto": producto, "stock": _stock[producto]}


def quitar(producto, cantidad):
    _validar(producto, cantidad)
    with _lock:
        actual = _stock.get(producto, 0)
        if actual < cantidad:
            raise ErrorDominio(f"stock insuficiente, hay {actual}")
        _stock[producto] = actual - cantidad
        return {"producto": producto, "stock": _stock[producto]}

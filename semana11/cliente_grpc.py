"""
Cliente gRPC del servicio, semana 11.

Uso
  python cliente_grpc.py listar
  python cliente_grpc.py agregar tornillo 25
  python cliente_grpc.py quitar tornillo 5 --reintentos 2

Variables
  SERVIDOR_HOST    (servidor)   SERVIDOR_PUERTO (50051)
  TIMEOUT_CLIENTE  (2)          deadline de cada intento, en segundos
  REINTENTOS       (0)          intentos extra ante DEADLINE_EXCEEDED o UNAVAILABLE

Cada reintento manda el MISMO id_solicitud.
"""
import argparse
import os
import uuid

import grpc

import servicio_pb2 as pb
import servicio_pb2_grpc as pb_grpc

HOST = os.getenv("SERVIDOR_HOST", "servidor")
PUERTO = os.getenv("SERVIDOR_PUERTO", "50051")
REINTENTABLES = {grpc.StatusCode.DEADLINE_EXCEEDED, grpc.StatusCode.UNAVAILABLE}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("metodo", choices=["listar", "agregar", "quitar"])
    ap.add_argument("producto", nargs="?", default="")
    ap.add_argument("cantidad", nargs="?", type=int, default=0)
    ap.add_argument("--reintentos", type=int, default=int(os.getenv("REINTENTOS", "0")))
    ap.add_argument("--timeout", type=float, default=float(os.getenv("TIMEOUT_CLIENTE", "2")))
    a = ap.parse_args()

    canal = grpc.insecure_channel(f"{HOST}:{PUERTO}")
    stub = pb_grpc.InventarioStub(canal)        # el stub, generado desde el .proto

    if a.metodo == "listar":
        llamada, solicitud = stub.Listar, pb.ListarSolicitud()
    else:
        solicitud = pb.MovimientoSolicitud(
            id_solicitud=uuid.uuid4().hex[:8], producto=a.producto, cantidad=a.cantidad)
        llamada = stub.Agregar if a.metodo == "agregar" else stub.Quitar

    for intento in range(1, a.reintentos + 2):
        ids = getattr(solicitud, "id_solicitud", "-")
        print(f"[cliente] intento {intento}, id_solicitud={ids}, deadline {a.timeout:.0f} s")
        try:
            resp = llamada(solicitud, timeout=a.timeout)
        except grpc.RpcError as e:
            print(f"[cliente]   {e.code().name}, {e.details()}")
            if e.code() in REINTENTABLES:
                continue
            return 1
        if a.metodo == "listar":
            print("[cliente]   " + (", ".join(f"{i.producto}={i.stock}" for i in resp.items) or "(vacío)"))
        else:
            print(f"[cliente]   OK {resp.producto} stock={resp.stock}")
        return 0
    if a.metodo == "listar":
        print("[cliente] me rendí, sin respuesta del servidor")
    else:
        print("[cliente] me rendí, la operación quedó en estado DESCONOCIDO")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

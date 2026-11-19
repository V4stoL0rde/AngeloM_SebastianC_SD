"""
Objetos remotos del servicio, semana 12 (Dominio: Sensores IoT).

  ControlSensores  objeto de entrada, se registra en el servidor de nombres.
                   Delega en dominio.py y fabrica objetos LoteSensores.
  LoteSensores     objeto con estado propio (lecturas pendientes). No se
                   registra con nombre; el cliente lo recibe POR REFERENCIA
                   desde ControlSensores.abrir_lote().
"""
import os
import threading
import time

from Pyro5.api import behavior, current_context, expose

import dominio

MODO = os.environ.get("MODO", "single")
POR_VALOR = os.environ.get("POR_VALOR", "0") == "1"

_contador_instancias = 0
_lock_contador = threading.Lock()


def _nueva_instancia():
    global _contador_instancias
    with _lock_contador:
        _contador_instancias += 1
        return _contador_instancias


@expose
class LoteSensores:
    """Lote de actualizaciones de sensores en curso. Su estado vive en el servidor.

    El cliente nunca recibe una copia, sino una referencia remota (un proxy).
    Al confirmar o cancelar, el lote se desregistra del daemon y cualquier
    referencia que quede apuntando a él pasa a ser una referencia colgante.
    """

    def __init__(self, cliente):
        self.cliente = cliente
        self.lecturas = []
        self.creado = time.strftime("%H:%M:%S")

    def agregar(self, sensor, valor):
        """Agrega una lectura (sensor, valor) al lote pendiente. Cambia estado del lote."""
        if not sensor:
            raise dominio.ErrorParametros("el sensor no puede estar vacío")
        if not valor:
            raise dominio.ErrorParametros("el valor no puede estar vacío")
        self.lecturas.append((sensor, str(valor)))
        return len(self.lecturas)

    def ver(self):
        """Consulta el estado actual del lote sin modificarlo."""
        return {
            "cliente": self.cliente,
            "creado": self.creado,
            "lecturas": [list(item) for item in self.lecturas],
        }

    def confirmar(self):
        """Aplica todas las lecturas al dominio y termina la vida del objeto. Cambia estado."""
        aplicados = {}
        for sensor, valor in self.lecturas:
            res = dominio.actualizar(sensor, valor)
            aplicados[res["sensor"]] = res["valor"]
        self._terminar()
        return aplicados

    def cancelar(self):
        """Descarta el lote sin modificar los sensores y termina su vida. Cambia estado."""
        self._terminar()
        return "cancelado"

    def _terminar(self):
        self._pyroDaemon.unregister(self)


@expose
@behavior(instance_mode=MODO)
class ControlSensores:
    """Objeto de entrada del servicio de sensores IoT. Se publica en el NameServer."""

    def __init__(self):
        self.numero = _nueva_instancia()
        self.llamadas = 0

    def _contar(self):
        self.llamadas += 1

    def listar(self):
        """Consulta todos los sensores y sus valores. No cambia estado."""
        self._contar()
        return dominio.listar()

    def actualizar(self, sensor, valor):
        """Crea o modifica el valor de un sensor. Cambia estado."""
        self._contar()
        return dominio.actualizar(sensor, str(valor))

    def leer(self, sensor):
        """Consulta el valor de un sensor específico. No cambia estado."""
        self._contar()
        return dominio.leer(sensor)

    def eliminar(self, sensor):
        """Elimina un sensor existente del registro. Cambia estado."""
        self._contar()
        return dominio.eliminar(sensor)

    def quien_soy(self):
        """Consulta qué instancia atendió la llamada y cuántas lleva. Cambia contador interno."""
        self._contar()
        return {
            "modo": MODO,
            "instancia": self.numero,
            "llamadas": self.llamadas,
            "cliente": str(current_context.client_sock_addr),
        }

    def lotes_vivos(self):
        """Consulta cuántos objetos LoteSensores siguen registrados en el daemon. No cambia estado."""
        self._contar()
        return sum(
            1 for o in self._pyroDaemon.objectsById.values()
            if isinstance(o, LoteSensores)
        )

    def abrir_lote(self, cliente):
        """Fábrica. Crea un LoteSensores en el servidor y entrega una referencia remota."""
        self._contar()
        lote = LoteSensores(cliente)
        if POR_VALOR:
            return lote
        self._pyroDaemon.register(lote)
        return lote
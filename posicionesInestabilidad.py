import os
import sys

ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ruta_proyecto not in sys.path:
    sys.path.append(ruta_proyecto)

from protocolV1_1.protocol_layer_two_content import *
from abc import ABC, abstractmethod
import time

import colored_logger
import logging
import colorama as cr
logger = colored_logger.Logger("posInes", logging.DEBUG, cr.Fore.CYAN)
logger.add_stderr(level=logging.ERROR)


H_TXT_LEN = 8
def myfmt(log: str) -> str:
    return log.ljust(H_TXT_LEN)

class State(ABC):
    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, context) -> None:
        self._context = context
    

    @abstractmethod
    def new_message(self, posiciones : "list[posiciones_data_tuple]") -> None:
        pass
    
    def on_entry(self) -> None:
        """Override to implement entry actions."""
        pass

    def on_exit(self) -> None:
        """Override to implement exit actions."""
        pass    

"""
    Aqui inicia, no hay data en posiciones
"""
class NoData(State):
    def new_message(self, posiciones : "list[posiciones_data_tuple]"):
        if len(posiciones) > 1 :
            self.context.position = posiciones
            self.context.transition_to(Active())
        self.context.position = posiciones
"""
    Hay >1 data en posiciones.
    - Aqui actualizamos la data siempre
"""
class Active(State):
    def new_message(self, posiciones : "list[posiciones_data_tuple]") -> None:
        if len(posiciones) <= 1 :
            self.context.transition_to(Intermitencia())
        else:
            self.context.position = posiciones

"""
    Aqui llegamos por una presunta intermitencia, que podria ser simplemente el FIN.
    - Aqui llega cuando hay data y de un momento a otro baja a 0. aqui se mantendra la data por tres minutos.
    - Si llega data regresamos a Active
"""
class Intermitencia(State):
    def on_entry(self) -> None:
        self._context._timeout = time.perf_counter() + 3*60

    def new_message(self, posiciones : "list[posiciones_data_tuple]") -> None:
        if len(posiciones) > 1 :
            self.context.position = posiciones
            self.context.transition_to(Active())
        else:      
            if self._context._timeout - time.perf_counter()  < 0:
                logger.debug(f"{myfmt('timeout1')}::{self.context.imei} timeout {self._context._timeout} - { time.perf_counter() }")
                self.context.position = posiciones
                self.context.transition_to(NoData())
            


class PosicionesFixer:
    def __init__(self, state = None ) -> None:
        self.imei = "NN"
        self._timeout = False
        self._state = None
        self._timeout = 0
        self._posiciones = []
        self._old_posiciones = []
        self.transition_to( state if state else NoData() )
    
    def set_imei(self, imei: str):
        self.imei = imei

    def transition_to(self, state: State):
        logger.debug(f"{myfmt('timeout1')}::{self.imei} transition_to \"{state.__class__.__name__}\"")
        if self._state is not None:
            self._state.on_exit()
        self._state = state
        self._state.context = self
        self._state.on_entry()

    def new_message(self, posiciones : "list[posiciones_data_tuple]"):
        self._state.new_message(posiciones)

    @property
    def position(self):
        return self._posiciones
    
    """
        Aqui solo vemos si el dato es diferente y guardamos para comparar
    """
    @position.setter
    def position(self, posiciones : "list[posiciones_data_tuple]"):        
        self._posiciones = posiciones


    def position_equal( self, new_posiciones: "list[posiciones_data_tuple]"):
        if len(self._posiciones) != len(new_posiciones):
            return False
        
        for z0, z1 in zip(self._posiciones, new_posiciones):
            if z0 != z1:
                return True


if "__main__" == __name__:
    posicion0 = posiciones_data_tuple(1, b"B3I-752", -5)
    posicion1 = posiciones_data_tuple(1, b"BAW-915", -6)
    posicion3 = posiciones_data_tuple(1, b"AAU-821", -7)
    posicion3 = posiciones_data_tuple(1, b"AWT-708", -8)
    posicion4 = posiciones_data_tuple(1, b"AHP-813", -9)
    posicion5 = posiciones_data_tuple(1, b"BAW-914", -0)

    posiciones = [ posicion0, posicion1, posicion3, posicion4, posicion5 ]
    buff = posiciones_data.write(posiciones)
    print(echos.bytearray2str(buff))
    BposicionesLen = len(buff)/5
    print(buff)
    buff = posiciones_data.read(buff)
    for placa in buff:
        print(placa)
    print("POSICIONES FIN \n\n")


    posicionesFixer = PosicionesFixer()
    posicionesFixer.new_message([])
    print("p vacio", len(posicionesFixer._posiciones))
    posicionesFixer.new_message([])
    print("p vacio", len(posicionesFixer._posiciones))
    posicionesFixer.new_message(buff)
    print("p full", len(posicionesFixer._posiciones))
    time.sleep(1)
    posicionesFixer.new_message([])
    print("p full", len(posicionesFixer._posiciones))
    time.sleep(1)
    posicionesFixer.new_message([])
    print("p full", len(posicionesFixer._posiciones))
    posicionesFixer.new_message([])
    print("p full", len(posicionesFixer._posiciones))
    time.sleep(18)
    posicionesFixer.new_message([])
    print("p full", len(posicionesFixer._posiciones))
    posicionesFixer.new_message([])
    print("p full", len(posicionesFixer._posiciones))
    time.sleep(3)
    posicionesFixer.new_message([])
    print("p vacio", len(posicionesFixer._posiciones))
    posicionesFixer.new_message(buff)
    print("p full", len(posicionesFixer._posiciones))
    
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


class PosicionesKeeper:
    def __init__(self):
        self.b_before3 = None
        self.b_before2 = None
        self.b_before1 = None
        self.b_current = None
        self.b_next2 = None
        self.b_next1 = None
        self.c_before3 = None
        self.c_before2 = None
        self.c_before1 = None
        self.c_current = None
        self.c_next2 = None
        self.c_next1 = None

    # 0: next 1: current 2: before
    def process(self, posiciones : "list[posiciones_data_tuple]") -> "list[posiciones_data_tuple]":
        # reading before
        if len(posiciones) == 0:
            return posiciones
        n_before  = 0
        n_next    = 0
        n_current = 0
        for pos in posiciones:
            if pos.type == 2:
                n_before = n_before + 1
            if pos.type == 0:
                n_next = n_next +1
            if pos.type == 1:
                n_current = 1
    
        if n_before == 0:
            self.c_before3 = None
            self.c_before2 = None
            self.c_before1 = None
        elif n_before == 1:
            self.c_before3 = posiciones[0]
            self.c_before2 = None
            self.c_before1 = None
        elif n_before == 2:
            self.c_before3 = posiciones[0]
            self.c_before2 = posiciones[1]
            self.c_before1 = None
        elif n_before == 3:
            self.c_before3 = posiciones[0]
            self.c_before2 = posiciones[1]
            self.c_before1 = posiciones[2]
        else:
            logger.error("n_before+3?")
            
        if n_next == 0:
            self.c_next2 = None
            self.c_next1 = None
        elif n_next == 1:
            self.c_next2 = posiciones[n_before+1]
            self.c_next1 = None
        elif n_next == 2:
            self.c_next2 = posiciones[n_before+1]
            self.c_next1 = posiciones[n_before+2]
        else:
            logger.error("c_next1+3?")

        self.c_current = posiciones[n_before]

        ## PARCHE LOGICA
        self.c_before3 = self.b_before3 if self.c_before3 == None else self.c_before3
        self.c_before2 = self.b_before2 if self.c_before2 == None else self.c_before2
        self.c_before1 = self.b_before1 if self.c_before1 == None else self.c_before1
        self.c_current = self.b_current if self.c_current == None else self.c_current
        self.c_next2   = self.b_next2 if self.c_next2 == None else self.c_next2
        self.c_next1   = self.b_next1 if self.c_next1 == None else self.c_next1

        ## UPDATE
        self.b_before3 = self.c_before3
        self.b_before2 = self.c_before2
        self.b_before1 = self.c_before1
        self.b_current = self.c_current
        self.b_next2   = self.c_next2
        self.b_next1   = self.c_next1

        ## Return
        arr = []
        if self.c_before3:
            arr.append(self.c_before3)
        if self.c_before2:
            arr.append(self.c_before2)
        if self.c_before1:
            arr.append(self.c_before1)  
        if self.c_current:
            arr.append(self.c_current) 
        if self.c_next2:
            arr.append(self.c_next2) 
        if self.c_next1:
            arr.append(self.c_next1) 

        return arr

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
    
import os
import sys

ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ruta_proyecto not in sys.path:
    sys.path.append(ruta_proyecto)

class alerta_request():         #no hay
    def __init__(self, buf):
        self.buf = buf    
    @staticmethod
    def write(**kwargs):
        return bytearray()

class authentication_request(): #no hay
    def __init__(self, buf):
        pass    
    @staticmethod
    def write(**kwargs):
        return bytearray()

class tarifa_request():         #si hay
    def __init__(self, buf):
        self.buf = buf
    def read(self):
        pass
    @staticmethod
    def write(**kwargs):
        return bytearray()

class tickets_request():        #si hay
    def __init__(self, buf):
        self.buf = buf
    def read(self):
        pass
    @staticmethod
    def write(**kwargs):
        return bytearray()

class hoja_de_ruta_request():   #si hay
    def __init__(self, buf):
        self.buf = buf
    def read(self):
        pass
    @staticmethod
    def write(**kwargs):
        return bytearray()

class posiciones_request():     #si hay
    def __init__(self, buf):
        self.buf = buf
    def read(self):
        pass
    @staticmethod
    def write(**kwargs):
        return bytearray()

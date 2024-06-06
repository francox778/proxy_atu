import os
import sys

ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ruta_proyecto not in sys.path:
    sys.path.append(ruta_proyecto)
    
# debo leer un mensaje completo. para eso esta el campo len. opcional el CRC
# voy a recibir en un thread. data secuencialmente . un select para el solito.



# Esto es todo lo que ve este archivo.


#  ____________________________________
# |     |        |         |     |     |
# | SOF |  Len   | CONTENT | CRC | EOF |
# |_____|________|_________|_____|_____|
#   1B      2B       1B       4B    1B


import socket
from enum import Enum
import queue
import time
import selectors
import protocolV1_1.protocol_headers as protocol_headers
import echos

import struct


import colored_logger
import logging
import colorama as cr

logger = colored_logger.Logger("prtcl_io", logging.INFO, cr.Fore.YELLOW)
logger.add_stderr(level=logging.ERROR)

MAX_LEN = 2000



class read_state(Enum):
    SYNC = 0
    HEADER = 1 
    DATA    = 2
    FOOTER  =3


class TimeOutException(Exception):
    pass
class ValidMessageException(Exception):
    pass
class ClosedSocketException(Exception):
    pass



class packet_reader():
    def __init__(self, sock, crc_check = False):
        self.read_state = read_state.SYNC
        self.recv_buf = bytearray()
        self.sock = sock
        self.sel = selectors.DefaultSelector()
        self.sel.register(sock, events = selectors.EVENT_READ, data=None)
        self.queue = queue.Queue()  
        self._packet_len = bytearray()     
        self._packet_data = bytearray()
        self._crc_check = crc_check

    def write(self , data):  
        # encapsular el paquete header y footer
        data_len = len(data)
        header = struct.pack(f"{protocol_headers.ENDIANESS}BH", protocol_headers.SOF, data_len)
        footer = struct.pack(f"{protocol_headers.ENDIANESS}HB", 0x0000, protocol_headers.EOF)
        logger.debug(echos.bytearray2str(header + data + footer))
        self.sock.send(header + data + footer)

    def readBlocking(self, timeout: float):
        try:
            start = time.perf_counter()
            while True:
                events = self.sel.select(timeout = timeout)
                for _, mask in events:
                    if mask & selectors.EVENT_READ:
                        self._read()
                        self._process()
                if time.perf_counter() - start >  timeout:
                    raise TimeOutException()
        except:
            raise


    def read(self):
        pass
 
    def send(self):
        pass

    def _read(self):
        try:
            data = self.sock.recv(1024)
        except BlockingIOError:
            pass
        else:
            if data:
                self.recv_buf.extend(data)
            else:
                raise ClosedSocketException("closed")




    def _process(self):
        if self.read_state == read_state.SYNC:
            while len(self.recv_buf) > 0: 
                self._process_sync()
                if self.read_state != read_state.SYNC:
                    break     

        if self.read_state == read_state.HEADER:
            self._process_header()
        if self.read_state == read_state.DATA:
            self._process_data()
        if self.read_state == read_state.FOOTER:
            self._process_footer()

    def _process_sync(self): 
        # primero leemos el sync.
        if self.recv_buf[0] == protocol_headers.SOF:
            self.read_state = read_state.HEADER
        self.recv_buf = self.recv_buf[1:]
        
    def _process_header(self):
        if len(self.recv_buf) >= 2:
            self._packet_len  = struct.unpack(f"{protocol_headers.ENDIANESS}H", self.recv_buf[0:2])[0]
            self.recv_buf = self.recv_buf[2:]
            self.read_state = read_state.DATA
            if self._packet_len > 2000:
                logger.error(f" longitud del paquete muy largo {self._packet_len}")

    def _process_data(self):
        if len(self.recv_buf) >= self._packet_len:
            self._packet_data = self.recv_buf[:self._packet_len]
            self.recv_buf = self.recv_buf[self._packet_len:]
            self.read_state = read_state.FOOTER


    def _process_footer(self): 
        if len(self.recv_buf) >= protocol_headers.FOOTER_LEN:
            crc_val  = struct.unpack(f"{protocol_headers.ENDIANESS}H", self.recv_buf[0:2])[0]
            eof = self.recv_buf[2]
            self.recv_buf = self.recv_buf[protocol_headers.FOOTER_LEN:]
            self.read_state = read_state.SYNC

            packet = self._packet_data
            if self._crc_check:
                #check crc...
                self.queue.put(packet, block=False)
                raise ValidMessageException()
            else:
                self.queue.put(packet, block=False)
                raise ValidMessageException()
        
    def getPacket(self):
        try: 
            return self.queue.get(block=False)
        except queue.Empty:
            return None
        



if __name__ == "__main__":
    
    HOST = '127.0.0.1'
    PORT = 22222 

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            io = packet_reader(conn)
            print(f"Connected by {addr}")
            while True:
                try:   
                    io.readBlocking(10)
                except ValidMessageException:
                    packet = io.getPacket()
                    print(b"recibido" + packet)
                except TimeOutException:
                    pass
                except (ClosedSocketException, Exception):
                    raise RuntimeError("conexion cerrada")
                finally:
                    pass 
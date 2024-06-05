import socket
import time
import traceback
import threading
import queue

import colorama as cr
import logging
import colored_logger
import protocolV1_1.protocol_io as io
import protocolV1_1.protocol_layer_one as prtcl
import protocolV1_1.protocol_layer_two_content as content
import protocolV1_1.protocol_layer_two_request as request

import protocolV1_1.protocol_headers as prtcl_h
from translator_atu_http import ThttpRequests as thttp

import atuHttp

logger = colored_logger.Logger("main", logging.DEBUG, cr.Fore.CYAN)

import socket
import time

import struct
import json

doc={}
doc["imei"] = "866989058575975"
doc["project"] = "test_project" #  //no es necesario..
doc["ota"]= "true"
doc["cmd"]= "true"
doc["sw"] = "6.6.6"
doc["hw"] = "1.1"
doc["otaV"] = "1.0"

#print(json.dumps(doc))
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect(('127.0.0.1',22222)) #localhost, 22222 ('18.229.227.108',65431)
clientsocket.settimeout(100)



###########################    Simulado Device OTA    ###################################
def deviceInfo(data):
    return json.dumps(data)


if __name__ == "__main__" :
    try:
        while True:
            #clientsocket.send((json.dumps(doc).encode()))
            comm = io.packet_reader(sock=clientsocket)

            Blogin = prtcl.Imain.loginW( prtcl.login_tuple(ver=1, imei=866989058568582, pattern_code=b"4053", token=b"")) # correcto
            #Blogin = prtcl.Imain.loginW( prtcl.login_tuple(ver=1, imei=866989058568582, pattern_code=b"4013", token=b"")) #incorrecto
            Blogout = prtcl.Imain.logoutW()
            Bping = prtcl.Imain.pingW(prtcl.ping_tuple( time.perf_counter_ns() ))
            Balerta = prtcl.Icontent.alertaW(content.alerta_data_tuple(timestamp= int(time.time())))
            Btarifa = prtcl.Irequest.tarifaW()
            Bhojaderuta = prtcl.Irequest.hoja_de_rutaW()
            BPosiciones = prtcl.Irequest.posicionesW()
            
            arr = [
                Blogin,     #0
                Blogout,    #1
                Bping,      #2
                Balerta,    #3
                Btarifa,    #4
                Bhojaderuta,#5
                BPosiciones #6
            ]

            while True:
                try:
                    opt = input("Intruduce una opcion.")
                    opt = int(opt)%8
                    logger.debug(f" opcion data")
                    comm.write(arr[opt])
                except ValueError as e:
                    logger.debug(f" {e} ")
    except Exception as e:
        logger.error(f"saliendo {e}", exc_info=True)


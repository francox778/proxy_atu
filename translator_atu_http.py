from protocol2http import protocol2http
from http2protocol import http2protocol
import atuHttp
from protocolV1_1.protocol_layer_two_content import *
from protocolV1_1.protocol_layer_one import *
import json
import time
from typing import Union

import logging
import colorama as cr
import colored_logger

# auth_json.get('datas',{}).get('user', {}).get('name')
logger = colored_logger.Logger("thttp", logging.DEBUG, cr.Fore.RED)
logger.add_stderr(logging.ERROR)


class THttpError(Exception):
    """cuando es diferente a 200.
    """
    pass

class THttpAns(Exception):
    """cuando la respuesta tiene de status false.
    """
    pass

class THttpToken(Exception):
    """cuando el problema esta relacionado al toke"""
    pass

class ThttpRequests():
    @staticmethod
    def login(http: atuHttp.AtuHttp, data: login_tuple) :
        d = protocol2http.login(data)
        r = http.login(**d)
        code  = r.status_code
        if code != 200:
            raise THttpError(f"Error http {code}")

        if r.json().get("status") == False:
            raise THttpAns(f"Error {r.json()}")    
        
        http.setToken(r.json().get("data").get("token"))
        result = http2protocol.auth(r.json())
        return result
    
    @staticmethod
    def alerta(http: atuHttp.AtuHttp, alerta: alerta_data_tuple) :
        d = protocol2http.alerta(alerta.timestamp)
        r = http.alerta(**d)
        return r.status_code
    
    @staticmethod
    def hoja_de_ruta(http: atuHttp.AtuHttp) :
        r = http.hoja_de_ruta()
        r = http2protocol.hoja_de_ruta(r.json())
        return r
    
    @staticmethod
    def tarifa(http: atuHttp.AtuHttp) :
        r = http.tarifa()
        r = http2protocol.tarifa(r.json())
        return r
    
    @staticmethod
    def posiciones(http: atuHttp.AtuHttp) :
        r = http.posiciones()
        r = http2protocol.obtener_posiciones(r.json())
        return r

    @staticmethod
    def tickets(http: atuHttp.AtuHttp, t: "list[tickets_data_tuple]"):
        d = protocol2http.tickets(t)
        r = http.tickets_generados(**d)
        code  = r.status_code
        if code != 200:
            raise THttpError(f"Error http {code}")

        if r.json().get("status") == False:
            raise THttpAns(f"Error {r.json()}") 
        return r



if __name__ == "__main__":
    http = atuHttp.AtuHttp( base_url = "https://billingws.gpstracking.pe/v1/api/" ) 
    auth = ThttpRequests.login(http, "4053", "866989058568582")
    print(auth)

    alerta = alerta_data_tuple(int(time.time()))
    result = ThttpRequests.alerta(http, alerta)
    print(result)
    
    result = ThttpRequests.tarifa(http)
    print(result)
    
    result = ThttpRequests.hoja_de_ruta(http)
    print(result)
    
    result = ThttpRequests.posiciones(http)
    print(result)
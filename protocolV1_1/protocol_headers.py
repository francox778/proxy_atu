import os
import sys

ruta_proyecto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ruta_proyecto not in sys.path:
    sys.path.append(ruta_proyecto)

from enum import Enum

FOOTER_LEN = 3
SOF = 0xAA
EOF = 0xBB

ENDIANESS = "<" 

class response(Enum):
	ACK = 0
	NACK = 0

class error_codes(Enum):
	OK = 0
	ID_ERRONEO = 1
	SERVICIO_NO_DISPONIBLE = 2
	NOT_SPECIFIED = 3
	VUELVE_A_CONECTAR  = 7	# Esto sale cuando status es false.
	IMEI_NO_REGISTRADO = 4
	TICKETS_RECIBIDOS  = 5
	TICKETS_RECIBIDOS_ERROR = 6
	ALERTA_NO_ENVIADA  = 8
	ALERTA_ENVIADA 	   = 9
	POSICIONES_ERROR   = 10
	POSICIONES_OK	   = 11
	HOJA_DE_RUTA_ERROR = 12
	HOJA_DE_RUTA_OK	   = 13
	TARIFA_ERROR 	   = 14
	TARIFA_OK		   = 15
	CONEXION_IS_NOT_LOGGED = 16  # Simplemente enviara un login, con el supuesto token que tiene
	

class packet_type(Enum):
	LOGIN = 0	  
	LOGOUT = 1
	PING = 2	   
	CMD = 3	 	  
	RESPONSE = 4  
	REQUEST = 5	  
	DATA = 6  

class content_type(Enum):
	ALERTA = 0
	AUTHENTICATION = 1
	TARIFA = 2
	TICKETS = 3
	HOJA_DE_RUTA = 4
	POSICIONES = 5



#
#  _____________________________________________
# |     |        | Packet |         |     |     |
# | SOF |  Len   | Type   | CONTENT | CRC | EOF |
# |_____|________|________|_________|_____|_____|
#   1B      2B       1B        1B     4B    1B
#